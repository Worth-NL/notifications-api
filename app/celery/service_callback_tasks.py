import json
import os
from urllib.parse import urlparse

from flask import current_app
from requests import HTTPError, RequestException, request

from app import notify_celery, signing
from app.config import QueueNames
from app.utils import DATETIME_FORMAT


@notify_celery.task(bind=True, name="send-delivery-status", max_retries=5, default_retry_delay=300)
def send_delivery_status_to_service(self, notification_id, encoded_status_update):
    status_update = signing.decode(encoded_status_update)

    data = {
        "id": str(notification_id),
        "reference": status_update["notification_client_reference"],
        "to": status_update["notification_to"],
        "status": status_update["notification_status"],
        "created_at": status_update["notification_created_at"],
        "completed_at": status_update["notification_updated_at"],
        "sent_at": status_update["notification_sent_at"],
        "notification_type": status_update["notification_type"],
        "template_id": status_update["template_id"],
        "template_version": status_update["template_version"],
    }

    _send_data_to_service_callback_api(
        self,
        data,
        status_update["service_callback_api_url"],
        status_update["service_callback_api_bearer_token"],
        "send_delivery_status_to_service",
    )


@notify_celery.task(bind=True, name="send-complaint", max_retries=5, default_retry_delay=300)
def send_complaint_to_service(self, complaint_data):
    complaint = signing.decode(complaint_data)

    data = {
        "notification_id": complaint["notification_id"],
        "complaint_id": complaint["complaint_id"],
        "reference": complaint["reference"],
        "to": complaint["to"],
        "complaint_date": complaint["complaint_date"],
    }

    _send_data_to_service_callback_api(
        self,
        data,
        complaint["service_callback_api_url"],
        complaint["service_callback_api_bearer_token"],
        "send_complaint_to_service",
    )


def _send_data_to_service_callback_api(self, data, service_callback_url, token, function_name):
    notification_id = data["notification_id"] if "notification_id" in data else data["id"]
    try:
        request_kwargs = {
            "method": "POST",
            "url": service_callback_url,
            "data": json.dumps(data),
            "headers": {"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
            "timeout": 5,
        }

        converted_url = urlparse(service_callback_url).hostname.replace(".", "-")
        certificate_name = f"{converted_url}.pem"

        certificate_path = f"{current_app.config['SSL_CERT_DIR']}/{certificate_name}"

        if os.path.exists(certificate_path):
            current_app.logger.info(
                "Certificate [%s] found for [%s] , using as client certificate.", certificate_name, service_callback_url
            )
            request_kwargs["cert"] = certificate_path
        else:
            current_app.logger.warning(
                "Certificate [%s] not found for [%s], no client certificate used.",
                certificate_name,
                service_callback_url,
            )

        response = request(**request_kwargs)

        current_app.logger.info(
            "%s sending %s to %s, response %s",
            function_name,
            notification_id,
            service_callback_url,
            response.status_code,
        )
        response.raise_for_status()
    except RequestException as e:
        current_app.logger.warning(
            "%s request failed for notification_id: %s and url: %s. exception: %s",
            function_name,
            notification_id,
            service_callback_url,
            e,
        )
        if not isinstance(e, HTTPError) or e.response.status_code >= 500 or e.response.status_code == 429:
            try:
                self.retry(queue=QueueNames.CALLBACKS_RETRY)
            except self.MaxRetriesExceededError:
                current_app.logger.warning(
                    "Retry: %s has retried the max num of times for callback url %s and notification_id: %s",
                    function_name,
                    service_callback_url,
                    notification_id,
                )
        else:
            current_app.logger.warning(
                "%s callback is not being retried for notification_id: %s and url: %s. exception: %s",
                function_name,
                notification_id,
                service_callback_url,
                e,
            )


def create_delivery_status_callback_data(notification, service_callback_api):
    data = {
        "notification_id": str(notification.id),
        "notification_client_reference": notification.client_reference,
        "notification_to": notification.to,
        "notification_status": notification.status,
        "notification_created_at": notification.created_at.strftime(DATETIME_FORMAT),
        "notification_updated_at": (
            notification.updated_at.strftime(DATETIME_FORMAT) if notification.updated_at else None
        ),
        "notification_sent_at": notification.sent_at.strftime(DATETIME_FORMAT) if notification.sent_at else None,
        "notification_type": notification.notification_type,
        "service_callback_api_url": service_callback_api.url,
        "service_callback_api_bearer_token": service_callback_api.bearer_token,
        "template_id": str(notification.template_id),
        "template_version": notification.template_version,
    }
    return signing.encode(data)


def create_complaint_callback_data(complaint, notification, service_callback_api, recipient):
    data = {
        "complaint_id": str(complaint.id),
        "notification_id": str(notification.id),
        "reference": notification.client_reference,
        "to": recipient,
        "complaint_date": complaint.complaint_date.strftime(DATETIME_FORMAT),
        "service_callback_api_url": service_callback_api.url,
        "service_callback_api_bearer_token": service_callback_api.bearer_token,
    }
    return signing.encode(data)
