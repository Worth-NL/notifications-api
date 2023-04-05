from datetime import datetime

from botocore.exceptions import ClientError as BotoClientError
from flask import current_app
from notifications_utils.postal_address import PostalAddress
from sqlalchemy.orm.exc import NoResultFound

from app import dvla_client, notify_celery
from app.clients.email import EmailClientNonRetryableException
from app.clients.email.aws_ses import AwsSesClientThrottlingSendRateException
from app.clients.letter.dvla import (
    DvlaDuplicatePrintRequestException,
    DvlaRetryableException,
    DvlaThrottlingException,
)
from app.clients.sms import SmsClientResponseException
from app.config import QueueNames
from app.constants import (
    LETTER_TYPE,
    NOTIFICATION_SENDING,
    NOTIFICATION_TECHNICAL_FAILURE,
)
from app.dao import notifications_dao
from app.dao.notifications_dao import update_notification_status_by_id
from app.dao.provider_details_dao import (
    get_provider_details_by_notification_type,
)
from app.delivery import send_to_providers
from app.exceptions import NotificationTechnicalFailureException
from app.letters.utils import LetterPDFNotFound, find_letter_pdf_in_s3


@notify_celery.task(bind=True, name="deliver_sms", max_retries=48, default_retry_delay=300)
def deliver_sms(self, notification_id):
    try:
        current_app.logger.info("Start sending SMS for notification id: {}".format(notification_id))
        notification = notifications_dao.get_notification_by_id(notification_id)
        if not notification:
            raise NoResultFound()
        send_to_providers.send_sms_to_provider(notification)
    except Exception as e:
        if isinstance(e, SmsClientResponseException):
            current_app.logger.warning(
                "SMS notification delivery for id: {} failed".format(notification_id), exc_info=True
            )
        else:
            current_app.logger.exception("SMS notification delivery for id: {} failed".format(notification_id))

        try:
            if self.request.retries == 0:
                self.retry(queue=QueueNames.RETRY, countdown=0)
            else:
                self.retry(queue=QueueNames.RETRY)
        except self.MaxRetriesExceededError:
            message = (
                "RETRY FAILED: Max retries reached. The task send_sms_to_provider failed for notification {}. "
                "Notification has been updated to technical-failure".format(notification_id)
            )
            update_notification_status_by_id(notification_id, NOTIFICATION_TECHNICAL_FAILURE)
            raise NotificationTechnicalFailureException(message)


@notify_celery.task(bind=True, name="deliver_email", max_retries=48, default_retry_delay=300)
def deliver_email(self, notification_id):
    try:
        current_app.logger.info("Start sending email for notification id: {}".format(notification_id))
        notification = notifications_dao.get_notification_by_id(notification_id)
        if not notification:
            raise NoResultFound()
        send_to_providers.send_email_to_provider(notification)
    except EmailClientNonRetryableException as e:
        current_app.logger.exception(f"Email notification {notification_id} failed: {e}")
        update_notification_status_by_id(notification_id, "technical-failure")
    except Exception as e:
        try:
            if isinstance(e, AwsSesClientThrottlingSendRateException):
                current_app.logger.warning(f"RETRY: Email notification {notification_id} was rate limited by SES")
            else:
                current_app.logger.exception(f"RETRY: Email notification {notification_id} failed")

            self.retry(queue=QueueNames.RETRY)
        except self.MaxRetriesExceededError:
            message = (
                "RETRY FAILED: Max retries reached. "
                "The task send_email_to_provider failed for notification {}. "
                "Notification has been updated to technical-failure".format(notification_id)
            )
            update_notification_status_by_id(notification_id, NOTIFICATION_TECHNICAL_FAILURE)
            raise NotificationTechnicalFailureException(message)


@notify_celery.task(bind=True, name="deliver_letter", max_retries=55, retry_backoff=True, retry_backoff_max=300)
def deliver_letter(self, notification_id):
    # 55 retries with exponential backoff gives a retry time of approximately 4 hours
    current_app.logger.info(f"Start sending letter for notification id: {notification_id}")
    notification = notifications_dao.get_notification_by_id(notification_id, _raise=True)
    postal_address = PostalAddress(notification.to, allow_international_letters=True)

    try:
        file_bytes = find_letter_pdf_in_s3(notification).get()["Body"].read()
    except (BotoClientError, LetterPDFNotFound) as e:
        update_notification_status_by_id(notification_id, NOTIFICATION_TECHNICAL_FAILURE)
        raise NotificationTechnicalFailureException(
            f"Error getting letter from bucket for notification {notification_id}"
        ) from e

    try:
        dvla_client.send_letter(
            notification_id=str(notification.id),
            reference=str(notification.reference),
            address=postal_address,
            postage=notification.postage,
            service_id=str(notification.service_id),
            organisation_id=str(notification.service.organisation_id),
            pdf_file=file_bytes,
        )
        update_letter_to_sending(notification)
    except DvlaRetryableException as e:
        if isinstance(e, DvlaThrottlingException):
            current_app.logger.warning(f"RETRY: Letter notification {notification_id} was rate limited by DVLA")
        else:
            current_app.logger.exception(f"RETRY: Letter notification {notification_id} failed")

        try:
            self.retry()
        except self.MaxRetriesExceededError as e:
            update_notification_status_by_id(notification_id, NOTIFICATION_TECHNICAL_FAILURE)
            raise NotificationTechnicalFailureException(
                "RETRY FAILED: Max retries reached. The task deliver_letter failed for notification "
                f"{notification_id}. Notification has been updated to technical-failure"
            ) from e
    except Exception as e:
        if isinstance(e, DvlaDuplicatePrintRequestException):
            current_app.logger.warning(f"Duplicate deliver_letter task called for notification {notification_id}")
            return

        update_notification_status_by_id(notification_id, NOTIFICATION_TECHNICAL_FAILURE)
        raise NotificationTechnicalFailureException(f"Error when sending letter notification {notification_id}") from e


def update_letter_to_sending(notification):
    provider = get_provider_details_by_notification_type(LETTER_TYPE)[0]

    notification.status = NOTIFICATION_SENDING
    notification.sent_at = datetime.utcnow()
    notification.sent_by = provider.identifier

    notifications_dao.dao_update_notification(notification)
