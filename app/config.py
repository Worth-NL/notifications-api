import json
import os
from datetime import timedelta

from celery.schedules import crontab
from kombu import Exchange, Queue


class QueueNames:
    PERIODIC = "periodic-tasks"
    DATABASE = "database-tasks"
    SEND_SMS = "send-sms-tasks"
    SEND_EMAIL = "send-email-tasks"
    SEND_LETTER = "send-letter-tasks"
    RESEARCH_MODE = "research-mode-tasks"
    REPORTING = "reporting-tasks"
    JOBS = "job-tasks"
    RETRY = "retry-tasks"
    NOTIFY = "notify-internal-tasks"
    CREATE_LETTERS_PDF = "create-letters-pdf-tasks"
    CALLBACKS = "service-callbacks"
    CALLBACKS_RETRY = "service-callbacks-retry"
    LETTERS = "letter-tasks"
    SES_CALLBACKS = "ses-callbacks"
    SMS_CALLBACKS = "sms-callbacks"
    LETTER_CALLBACKS = "letter-callbacks"
    ANTIVIRUS = "antivirus-tasks"
    SANITISE_LETTERS = "sanitise-letter-tasks"
    BROADCASTS = "broadcast-tasks"
    GOVUK_ALERTS = "govuk-alerts"

    @staticmethod
    def all_queues():
        return [
            QueueNames.PERIODIC,
            QueueNames.DATABASE,
            QueueNames.SEND_SMS,
            QueueNames.SEND_EMAIL,
            QueueNames.SEND_LETTER,
            QueueNames.RESEARCH_MODE,
            QueueNames.REPORTING,
            QueueNames.JOBS,
            QueueNames.RETRY,
            QueueNames.NOTIFY,
            QueueNames.CREATE_LETTERS_PDF,
            QueueNames.CALLBACKS,
            QueueNames.CALLBACKS_RETRY,
            QueueNames.LETTERS,
            QueueNames.SES_CALLBACKS,
            QueueNames.SMS_CALLBACKS,
            QueueNames.LETTER_CALLBACKS,
            QueueNames.BROADCASTS,
        ]


class BroadcastProvider:
    EE = "ee"
    VODAFONE = "vodafone"
    THREE = "three"
    O2 = "o2"

    PROVIDERS = [EE, VODAFONE, THREE, O2]


class TaskNames:
    PROCESS_INCOMPLETE_JOBS = "process-incomplete-jobs"
    ZIP_AND_SEND_LETTER_PDFS = "zip-and-send-letter-pdfs"
    SCAN_FILE = "scan-file"
    SANITISE_LETTER = "sanitise-and-upload-letter"
    CREATE_PDF_FOR_TEMPLATED_LETTER = "create-pdf-for-templated-letter"
    PUBLISH_GOVUK_ALERTS = "publish-govuk-alerts"
    RECREATE_PDF_FOR_PRECOMPILED_LETTER = "recreate-pdf-for-precompiled-letter"


class Config:
    # URL of admin app
    ADMIN_BASE_URL = os.getenv("ADMIN_BASE_URL", "http://localhost:6012")

    # URL of api app (on AWS this is the internal api endpoint)
    API_HOST_NAME = os.getenv("API_HOST_NAME")
    API_HOST_NAME_INTERNAL = os.getenv("API_HOST_NAME_INTERNAL")

    # secrets that internal apps, such as the admin app or document download, must use to authenticate with the API
    ADMIN_CLIENT_ID = "notify-admin"
    FUNCTIONAL_TESTS_CLIENT_ID = "notify-functional-tests"

    INTERNAL_CLIENT_API_KEYS = json.loads(os.environ.get("INTERNAL_CLIENT_API_KEYS", "{}"))

    # encyption secret/salt
    SECRET_KEY = os.getenv("SECRET_KEY")
    DANGEROUS_SALT = os.getenv("DANGEROUS_SALT")

    # DB conection string
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

    # MMG API Key
    MMG_API_KEY = os.getenv("MMG_API_KEY")

    # MMG Callback URL for delivery receipts
    # If this is not set, MMG will send to the URL that they have set up in their system
    MMG_RECEIPT_URL = os.getenv("MMG_RECEIPT_URL")

    # Firetext API Key
    FIRETEXT_API_KEY = os.getenv("FIRETEXT_API_KEY")
    FIRETEXT_INTERNATIONAL_API_KEY = os.getenv("FIRETEXT_INTERNATIONAL_API_KEY", "placeholder")

    # Firetext Callback URL for delivery receipts
    # If this is not set, Firetext will send to the URL that is set in the Firetext dashboard
    FIRETEXT_RECEIPT_URL = os.getenv("FIRETEXT_RECEIPT_URL")

    # Spryng API key
    SPRYNG_API_KEY = os.environ.get("SPRYNG_API_KEY")

    # Prefix to identify queues in SQS
    NOTIFICATION_QUEUE_PREFIX = os.getenv("NOTIFICATION_QUEUE_PREFIX")

    # URL of redis instance
    REDIS_URL = os.getenv("REDIS_URL")
    REDIS_ENABLED = False if os.environ.get("REDIS_ENABLED") == "0" else True
    EXPIRE_CACHE_TEN_MINUTES = 600
    EXPIRE_CACHE_EIGHT_DAYS = 8 * 24 * 60 * 60

    # Zendesk
    ZENDESK_API_KEY = os.environ.get("ZENDESK_API_KEY")

    # Logging
    DEBUG = False

    NOTIFY_LOG_LEVEL = os.getenv("NOTIFY_LOG_LEVEL", "INFO")
    NOTIFY_LOG_LEVEL_HANDLERS = os.getenv("NOTIFY_LOG_LEVEL_HANDLERS", NOTIFY_LOG_LEVEL)

    NOTIFY_REQUEST_LOG_LEVEL = os.getenv("NOTIFY_REQUEST_LOG_LEVEL", "INFO")

    # Cronitor
    CRONITOR_ENABLED = os.environ.get("CRONITOR_ENABLED", "0") == "1"
    CRONITOR_KEYS = json.loads(os.environ.get("CRONITOR_KEYS", "{}"))

    # Antivirus
    ANTIVIRUS_ENABLED = True

    NOTIFY_EVENTLET_STATS = os.getenv("NOTIFY_EVENTLET_STATS", "0") == "1"

    ###########################
    # Default config values ###
    ###########################

    NOTIFY_ENVIRONMENT = os.environ.get("NOTIFY_ENVIRONMENT", "development")
    AWS_REGION = "eu-west-1"
    INVITATION_EXPIRATION_DAYS = 2
    NOTIFY_APP_NAME = "api"

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(os.environ.get("SQLALCHEMY_POOL_SIZE", 5)),
        "pool_timeout": 30,
        "pool_recycle": 300,
        "connect_args": {
            # statement_timeout is overridden in setup_sqlalchemy_events, but not all our
            # invocations heed those event hooks (e.g. alembic migrations), so this is set
            # as a fallback
            "options": "-c statement_timeout=1200000",
        },
    }
    DATABASE_DEFAULT_DISABLE_PARALLEL_QUERY = (
        os.getenv(
            "DATABASE_DEFAULT_DISABLE_PARALLEL_QUERY",
            "1",
        )
        == "1"
    )
    DATABASE_STATEMENT_TIMEOUT_MS = int(os.getenv("DATABASE_STATEMENT_TIMEOUT_MS", 1_200_000))

    PAGE_SIZE = 50
    API_PAGE_SIZE = 250
    TEST_MESSAGE_FILENAME = "Test message"
    ONE_OFF_MESSAGE_FILENAME = "Report"
    MAX_VERIFY_CODE_COUNT = 5
    MAX_FAILED_LOGIN_COUNT = 10

    # these should always add up to 100%
    SMS_PROVIDER_RESTING_POINTS = {"mmg": 0, "firetext": 0, "spryng": 100}

    NOTIFY_SERVICE_ID = "d6aa2c68-a2d9-4437-ab19-3ae8eb202553"
    NOTIFY_USER_ID = "6af522d0-2915-4e52-83a3-3690455a5fe6"
    INVITATION_EMAIL_TEMPLATE_ID = "b24bf0fa-dd64-4105-867c-4ed529e12df3"  # NL
    BROADCAST_INVITATION_EMAIL_TEMPLATE_ID = "86761e21-b39c-43e1-a06b-a3340bc2bc7a"  # NL
    SMS_CODE_TEMPLATE_ID = "f8209d70-9aa2-4a8c-89f9-00514492fa27"  # NL
    EMAIL_2FA_TEMPLATE_ID = "320a5f19-600f-451e-9646-11206c69828d"  # NL
    NEW_USER_EMAIL_VERIFICATION_TEMPLATE_ID = "afd325cd-c83e-4b0b-8426-7acb9c0aa62b"  # NL
    PASSWORD_RESET_TEMPLATE_ID = "4cc48b09-62d0-473f-8514-3023b306a0fb"  # NL
    ALREADY_REGISTERED_EMAIL_TEMPLATE_ID = "bb3c17a8-6009-4f67-a943-353982c15c98"  # NL
    CHANGE_EMAIL_CONFIRMATION_TEMPLATE_ID = "9eefb5bf-f1fb-46ce-9079-691260b0af9b"  # NL
    SERVICE_NOW_LIVE_TEMPLATE_ID = "ec92ba79-222b-46f1-944a-79b3c072234d"  # NL
    ORGANISATION_INVITATION_EMAIL_TEMPLATE_ID = "dfd254da-39d1-468f-bd0d-2c9e017c13a6"  # NL
    TEAM_MEMBER_EDIT_EMAIL_TEMPLATE_ID = "c73f1d71-4049-46d5-a647-d013bdeca3f0"
    TEAM_MEMBER_EDIT_MOBILE_TEMPLATE_ID = "8a31520f-4751-4789-8ea1-fe54496725eb"
    REPLY_TO_EMAIL_ADDRESS_VERIFICATION_TEMPLATE_ID = "2e542078-1b7e-4640-ab44-57e5db6b3bf3"  # NL
    MOU_SIGNER_RECEIPT_TEMPLATE_ID = "4fd2e43c-309b-4e50-8fb8-1955852d9d71"
    MOU_SIGNED_ON_BEHALF_SIGNER_RECEIPT_TEMPLATE_ID = "c20206d5-bf03-4002-9a90-37d5032d9e84"
    MOU_SIGNED_ON_BEHALF_ON_BEHALF_RECEIPT_TEMPLATE_ID = "522b6657-5ca5-4368-a294-6b527703bd0b"
    GO_LIVE_NEW_REQUEST_FOR_ORG_APPROVERS_TEMPLATE_ID = "5c7cfc0f-c3f4-4bd6-9a84-5a144aad5425"
    GO_LIVE_NEW_REQUEST_FOR_ORG_REQUESTER_TEMPLATE_ID = "c7083bfe-1b9a-4ff9-bd5c-30508727df6e"
    GO_LIVE_REQUEST_NEXT_STEPS_FOR_ORG_USER_TEMPLATE_ID = "62f12a62-742b-4458-9336-741521b131c7"
    GO_LIVE_REQUEST_REJECTED_BY_ORG_USER_TEMPLATE_ID = "507d0796-9e23-4ad7-b83b-5efbd9496866"
    NOTIFY_INTERNATIONAL_SMS_SENDER = "07984404008"
    LETTERS_VOLUME_EMAIL_TEMPLATE_ID = "11fad854-fd38-4a7c-bd17-805fb13dfc12"
    NHS_EMAIL_BRANDING_ID = "a7dc4e56-660b-4db7-8cff-12c37b12b5ea"
    NHS_LETTER_BRANDING_ID = "2cd354bb-6b85-eda3-c0ad-6b613150459f"
    REQUEST_INVITE_TO_SERVICE_TEMPLATE_ID = "77677459-f862-44ee-96d9-b8cb2323d407"
    RECEIPT_FOR_REQUEST_INVITE_TO_SERVICE_TEMPLATE_ID = "38bcd263-6ce8-431f-979d-8e637c1f0576"
    USER_RESEARCH_EMAIL_FOR_NEW_USERS_TEMPLATE_ID = "55bcb671-4924-46c5-a00d-1a9d48458008"
    SERVICE_JOIN_REQUEST_APPROVED_TEMPLATE_ID = "4d8ee728-100e-4f0e-8793-5638cfa4ffa4"
    # we only need real email in Live environment (production)
    DVLA_EMAIL_ADDRESSES = json.loads(os.environ.get("DVLA_EMAIL_ADDRESSES", "[]"))
    NOTIFY_SUPPORT_EMAIL_ADDRESS = "gov-uk-notify-support@digital.cabinet-office.gov.uk"

    CELERY = {
        "broker_url": "https://sqs.eu-west-1.amazonaws.com",
        "broker_transport": "sqs",
        "broker_transport_options": {
            "region": AWS_REGION,
            "visibility_timeout": 310,
            "queue_name_prefix": NOTIFICATION_QUEUE_PREFIX,
            "is_secure": True,
        },
        "result_expires": 0,
        "timezone": "UTC",
        "imports": [
            "app.celery.tasks",
            "app.celery.scheduled_tasks",
            "app.celery.reporting_tasks",
            "app.celery.nightly_tasks",
        ],
        # this is overriden by the -Q command, but locally, we should read from all queues
        "task_queues": [Queue(queue, Exchange("default"), routing_key=queue) for queue in QueueNames.all_queues()],
        "beat_schedule": {
            # app/celery/scheduled_tasks.py
            "run-scheduled-jobs": {
                "task": "run-scheduled-jobs",
                "schedule": crontab(minute="0,15,30,45"),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "delete-verify-codes": {
                "task": "delete-verify-codes",
                "schedule": timedelta(minutes=63),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "delete-invitations": {
                "task": "delete-invitations",
                "schedule": timedelta(minutes=66),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "generate-sms-delivery-stats": {
                "task": "generate-sms-delivery-stats",
                "schedule": crontab(),  # Every minute
                "options": {"queue": QueueNames.PERIODIC},
            },
            "switch-current-sms-provider-on-slow-delivery": {
                "task": "switch-current-sms-provider-on-slow-delivery",
                "schedule": crontab(),  # Every minute
                "options": {"queue": QueueNames.PERIODIC},
            },
            "check-job-status": {
                "task": "check-job-status",
                "schedule": crontab(),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "tend-providers-back-to-middle": {
                "task": "tend-providers-back-to-middle",
                "schedule": crontab(minute="*/5"),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "check-for-missing-rows-in-completed-jobs": {
                "task": "check-for-missing-rows-in-completed-jobs",
                "schedule": crontab(minute="*/10"),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "replay-created-notifications": {
                "task": "replay-created-notifications",
                "schedule": crontab(minute="0, 15, 30, 45"),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "run-populate-annual-billing": {
                "task": "run-populate-annual-billing",
                "schedule": crontab(minute=1, hour=2, day_of_month=1, month_of_year=4),
                "options": {"queue": QueueNames.PERIODIC},
            },
            # app/celery/nightly_tasks.py
            "timeout-sending-notifications": {
                "task": "timeout-sending-notifications",
                "schedule": crontab(hour=0, minute=5),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "archive-unsubscribe-requests": {
                "task": "archive-unsubscribe-requests",
                "schedule": crontab(hour=0, minute=5),
                "options": {"queue": QueueNames.REPORTING},
            },
            "create-nightly-billing": {
                "task": "create-nightly-billing",
                "schedule": crontab(hour=0, minute=15),
                "options": {"queue": QueueNames.REPORTING},
            },
            "update-ft-billing-for-today": {
                "task": "update-ft-billing-for-today",
                "schedule": crontab(hour="*", minute=0),
                "options": {"queue": QueueNames.REPORTING},
            },
            "create-nightly-notification-status": {
                "task": "create-nightly-notification-status",
                # after 'timeout-sending-notifications'
                "schedule": crontab(hour=0, minute=30),
                "options": {"queue": QueueNames.REPORTING},
            },
            "delete-notifications-older-than-retention": {
                "task": "delete-notifications-older-than-retention",
                # after 'create-nightly-notification-status'
                "schedule": crontab(hour=3, minute=0),
                "options": {"queue": QueueNames.REPORTING},
            },
            "delete-inbound-sms": {
                "task": "delete-inbound-sms",
                "schedule": crontab(hour=1, minute=40),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "save-daily-notification-processing-time": {
                "task": "save-daily-notification-processing-time",
                "schedule": crontab(hour=2, minute=0),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "remove_sms_email_jobs": {
                "task": "remove_sms_email_jobs",
                "schedule": crontab(hour=4, minute=0),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "remove_letter_jobs": {
                "task": "remove_letter_jobs",
                "schedule": crontab(hour=4, minute=20),
                # since we mark jobs as archived
                "options": {"queue": QueueNames.PERIODIC},
            },
            "check-if-letters-still-in-created": {
                "task": "check-if-letters-still-in-created",
                "schedule": crontab(day_of_week="mon-fri", hour=7, minute=0),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "check-if-letters-still-pending-virus-check-ten-minutely": {
                "task": "check-if-letters-still-pending-virus-check",
                "schedule": crontab(minute="*/10"),
                # check last half hour, every ten minutes
                "kwargs": {"max_minutes_ago_to_check": 30},
                "options": {"queue": QueueNames.PERIODIC},
            },
            "check-if-letters-still-pending-virus-check-nightly": {
                "task": "check-if-letters-still-pending-virus-check",
                "schedule": crontab(hour=20, minute=0),
                # check back two entire days, once per day, just in case things slipped through the net somehow
                "kwargs": {"max_minutes_ago_to_check": 60 * 24 * 2},
                "options": {"queue": QueueNames.PERIODIC},
            },
            "check-for-services-with-high-failure-rates-or-sending-to-tv-numbers": {
                "task": "check-for-services-with-high-failure-rates-or-sending-to-tv-numbers",
                "schedule": crontab(day_of_week="mon-fri", hour=10, minute=30),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "raise-alert-if-letter-notifications-still-sending": {
                "task": "raise-alert-if-letter-notifications-still-sending",
                "schedule": crontab(hour=19, minute=00),
                "options": {"queue": QueueNames.PERIODIC},
            },
            # The check-time-to-collate-letters does assume it is called in an hour that BST does not make a
            # difference to the truncate date which translates to the filename to process
            # We schedule it for 16:50 and 17:50 UTC. This task is then responsible for determining if the local time
            # is 17:50, and if so, actually kicking off letter collation.
            # If updating the cron schedule, you should update the task as well.
            "check-time-to-collate-letters": {
                "task": "check-time-to-collate-letters",
                "schedule": crontab(hour="16,17", minute=50),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "delete-old-records-from-events-table": {
                "task": "delete-old-records-from-events-table",
                "schedule": crontab(hour=3, minute=4),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "zendesk-new-email-branding-report": {
                "task": "zendesk-new-email-branding-report",
                "schedule": crontab(hour=0, minute=30, day_of_week="mon-fri"),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "check-for-low-available-inbound-sms-numbers": {
                "task": "check-for-low-available-inbound-sms-numbers",
                "schedule": crontab(hour=9, minute=0, day_of_week="mon"),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "weekly-dwp-report": {
                "task": "weekly-dwp-report",
                "schedule": crontab(hour=9, minute=0, day_of_week="mon"),
                "options": {"queue": QueueNames.REPORTING},
            },
            "weekly-user-research-email": {
                "task": "weekly-user-research-email",
                "schedule": crontab(hour=10, minute=0, day_of_week="wed"),
                "options": {"queue": QueueNames.PERIODIC},
            },
            # first tuesday of every month
            "change-dvla-api-key": {
                "task": "change-dvla-api-key",
                "schedule": crontab(hour=9, minute=0, day_of_week="tue", day_of_month="1-7"),
                "options": {"queue": QueueNames.PERIODIC},
            },
            # the wednesday immediately following the first tuesday of every month
            "change-dvla-password": {
                "task": "change-dvla-password",
                "schedule": crontab(hour=9, minute=0, day_of_week="wed", day_of_month="2-8"),
                "options": {"queue": QueueNames.PERIODIC},
            },
        },
    }

    # we can set celeryd_prefetch_multiplier to be 1 for celery apps which handle only long running tasks
    if os.getenv("CELERYD_PREFETCH_MULTIPLIER"):
        CELERY["worker_prefetch_multiplier"] = os.getenv("CELERYD_PREFETCH_MULTIPLIER")

    STATSD_HOST = os.getenv("STATSD_HOST")
    STATSD_PORT = 8125
    STATSD_ENABLED = bool(STATSD_HOST)

    SENDING_NOTIFICATIONS_TIMEOUT_PERIOD = 259200  # 3 days

    SIMULATED_EMAIL_ADDRESSES = (
        "simulate-delivered@notifications.service.gov.uk",
        "simulate-delivered-2@notifications.service.gov.uk",
        "simulate-delivered-3@notifications.service.gov.uk",
    )

    SIMULATED_SMS_NUMBERS = ("+31612345678", "+31623456789", "+31634567890")

    FREE_SMS_TIER_FRAGMENT_COUNT = 250000

    SMS_INBOUND_WHITELIST = json.loads(os.environ.get("SMS_INBOUND_WHITELIST", "[]"))
    FIRETEXT_INBOUND_SMS_AUTH = json.loads(os.environ.get("FIRETEXT_INBOUND_SMS_AUTH", "[]"))
    MMG_INBOUND_SMS_AUTH = json.loads(os.environ.get("MMG_INBOUND_SMS_AUTH", "[]"))
    MMG_INBOUND_SMS_USERNAME = json.loads(os.environ.get("MMG_INBOUND_SMS_USERNAME", "[]"))
    LOW_INBOUND_SMS_NUMBER_THRESHOLD = 50

    TEMPLATE_PREVIEW_API_HOST = os.environ.get("TEMPLATE_PREVIEW_API_HOST", "http://localhost:6013")
    TEMPLATE_PREVIEW_API_KEY = os.environ.get("TEMPLATE_PREVIEW_API_KEY", "my-secret-key")

    DOCUMENT_DOWNLOAD_API_HOST = os.environ.get("DOCUMENT_DOWNLOAD_API_HOST", "http://localhost:7000")
    DOCUMENT_DOWNLOAD_API_HOST_INTERNAL = os.environ.get("DOCUMENT_DOWNLOAD_API_HOST_INTERNAL", "http://localhost:7000")
    DOCUMENT_DOWNLOAD_API_KEY = os.environ.get("DOCUMENT_DOWNLOAD_API_KEY", "auth-token")

    MMG_URL = os.environ.get("MMG_URL", "https://api.mmg.co.uk/jsonv2a/api.php")
    FIRETEXT_URL = os.environ.get("FIRETEXT_URL", "https://www.firetext.co.uk/api/sendsms/json")
    SPRYNG_URL = os.environ.get("SPRYNG_URL", "https://rest.spryngsms.com/v1/messages")
    SES_STUB_URL = os.environ.get("SES_STUB_URL")

    CBC_PROXY_ENABLED = True
    CBC_PROXY_AWS_ACCESS_KEY_ID = os.environ.get("CBC_PROXY_AWS_ACCESS_KEY_ID", "")
    CBC_PROXY_AWS_SECRET_ACCESS_KEY = os.environ.get("CBC_PROXY_AWS_SECRET_ACCESS_KEY", "")

    ENABLED_CBCS = {BroadcastProvider.EE, BroadcastProvider.THREE, BroadcastProvider.O2, BroadcastProvider.VODAFONE}

    # as defined in api db migration 0331_add_broadcast_org.py
    BROADCAST_ORGANISATION_ID = "38e4bf69-93b0-445d-acee-53ea53fe02df"

    DVLA_API_BASE_URL = os.environ.get("DVLA_API_BASE_URL", "https://uat.driver-vehicle-licensing.api.gov.uk")
    DVLA_API_TLS_CIPHERS = os.environ.get("DVLA_API_TLS_CIPHERS")

    # We don't expect to have any zendesk reporting beyond this. If someone is looking here and thinking of adding
    # something new, let's consider a more holistic approach first please. We should be revisiting this approach in
    # Q1 2023.
    # Our manifest builder takes our JSON string from notifications-credentials and passes it through the Jinja2
    # `tojson` filter, which escapes things like ' < > to their \uxxxx form. We need to turn those back into
    # real characters. We do that by turning the env var unicode string to bytes and then decoding that back to
    # a unicode string via the unicode-escape encoding, which will automatically decode \uxxxx forms back to their
    # basic representation.
    ZENDESK_REPORTING = json.loads(os.environ.get("ZENDESK_REPORTING", "{}").encode().decode("unicode-escape"))

    NOTIFY_EMAIL_DOMAIN = os.environ.get("NOTIFY_EMAIL_DOMAIN")
    S3_BUCKET_CSV_UPLOAD = os.environ.get("S3_BUCKET_CSV_UPLOAD")
    S3_BUCKET_CONTACT_LIST = os.environ.get("S3_BUCKET_CONTACT_LIST")
    S3_BUCKET_TEST_LETTERS = os.environ.get("S3_BUCKET_TEST_LETTERS")
    S3_BUCKET_LETTERS_PDF = os.environ.get("S3_BUCKET_LETTERS_PDF")
    S3_BUCKET_LETTERS_SCAN = os.environ.get("S3_BUCKET_LETTERS_SCAN")
    S3_BUCKET_INVALID_PDF = os.environ.get("S3_BUCKET_INVALID_PDF")
    S3_BUCKET_TRANSIENT_UPLOADED_LETTERS = os.environ.get("S3_BUCKET_TRANSIENT_UPLOADED_LETTERS")
    S3_BUCKET_LETTER_SANITISE = os.environ.get("S3_BUCKET_LETTER_SANITISE")
    FROM_NUMBER = os.environ.get("FROM_NUMBER", "NotifyNL")
    API_RATE_LIMIT_ENABLED = os.environ.get("API_RATE_LIMIT_ENABLED", "1") == "1"

    SEND_LETTERS_ENABLED = os.environ.get("SEND_LETTERS_ENABLED", "0") == "1"
    REGISTER_FUNCTIONAL_TESTING_BLUEPRINT = os.environ.get("REGISTER_FUNCTIONAL_TESTING_BLUEPRINT", "0") == "1"
    SEND_ZENDESK_ALERTS_ENABLED = os.environ.get("SEND_ZENDESK_ALERTS_ENABLED", "0") == "1"
    CHECK_SLOW_TEXT_MESSAGE_DELIVERY = os.environ.get("CHECK_SLOW_TEXT_MESSAGE_DELIVERY", "0") == "1"
    WEEKLY_USER_RESEARCH_EMAIL_ENABLED = os.environ.get("WEEKLY_USER_RESEARCH_EMAIL_ENABLED", "0") == "1"


######################
# Config overrides ###
######################
class Development(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False

    SERVER_NAME = os.getenv("SERVER_NAME")

    REDIS_ENABLED = os.getenv("REDIS_ENABLED") == "1"

    S3_BUCKET_CSV_UPLOAD = "development-notifications-csv-upload-notifynl"
    S3_BUCKET_CONTACT_LIST = "development-contact-list-notifynl"
    S3_BUCKET_TEST_LETTERS = "development-test-letters-notifynl"
    S3_BUCKET_DVLA_RESPONSE = "notify.tools-ftp-notifynl"
    S3_BUCKET_LETTERS_PDF = "development-letters-pdf-notifynl"
    S3_BUCKET_LETTERS_SCAN = "development-letters-scan-notifynl"
    S3_BUCKET_INVALID_PDF = "development-letters-invalid-pdf-notifynl"
    S3_BUCKET_TRANSIENT_UPLOADED_LETTERS = "development-transient-uploaded-letters-notifynl"
    S3_BUCKET_LETTER_SANITISE = "development-letters-sanitise-notifynl"

    LOGO_CDN_DOMAIN = "d26j1qfpsndp6a.cloudfront.net"

    INTERNAL_CLIENT_API_KEYS = {
        Config.ADMIN_CLIENT_ID: ["dev-notify-secret-key"],
        Config.FUNCTIONAL_TESTS_CLIENT_ID: ["functional-tests-secret-key"],
    }

    SECRET_KEY = "dev-notify-secret-key"
    DANGEROUS_SALT = "dev-notify-salt"

    MMG_INBOUND_SMS_AUTH = ["testkey"]
    MMG_INBOUND_SMS_USERNAME = ["username"]

    NOTIFY_ENVIRONMENT = "development"
    NOTIFY_EMAIL_DOMAIN = "notifynl.nl"

    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql://localhost/notification_api")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    ANTIVIRUS_ENABLED = os.getenv("ANTIVIRUS_ENABLED") == "1"

    API_HOST_NAME = os.getenv("API_HOST_NAME", "http://localhost:6011")
    API_HOST_NAME_INTERNAL = os.getenv("API_HOST_NAME_INTERNAL", "http://localhost:6011")
    API_RATE_LIMIT_ENABLED = True
    DVLA_EMAIL_ADDRESSES = ["success@simulator.amazonses.com"]

    CBC_PROXY_ENABLED = False

    SSL_CERT_DIR = os.getenv("SSL_CERT_DIR")

    REGISTER_FUNCTIONAL_TESTING_BLUEPRINT = True

    FROM_NUMBER = "development"


class Test(Development):
    NOTIFY_EMAIL_DOMAIN = "test.notify.com"
    FROM_NUMBER = "testing"
    NOTIFY_ENVIRONMENT = "test"
    TESTING = True

    S3_BUCKET_CSV_UPLOAD = "test-notifications-csv-upload"
    S3_BUCKET_CONTACT_LIST = "test-contact-list"
    S3_BUCKET_TEST_LETTERS = "test-test-letters"
    S3_BUCKET_LETTERS_PDF = "test-letters-pdf"
    S3_BUCKET_LETTERS_SCAN = "test-letters-scan"
    S3_BUCKET_INVALID_PDF = "test-letters-invalid-pdf"
    S3_BUCKET_TRANSIENT_UPLOADED_LETTERS = "test-transient-uploaded-letters"
    S3_BUCKET_LETTER_SANITISE = "test-letters-sanitise"

    # when testing, the SQLALCHEMY_DATABASE_URI is used for the postgres server's location
    # but the database name is set in the _notify_db fixture
    SQLALCHEMY_RECORD_QUERIES = True

    CELERY = {**Config.CELERY, "broker_url": "you-forgot-to-mock-celery-in-your-tests://", "broker_transport": None}

    ANTIVIRUS_ENABLED = True

    API_RATE_LIMIT_ENABLED = True
    API_HOST_NAME = "http://localhost:6011"
    API_HOST_NAME_INTERNAL = "http://localhost:6011"

    SMS_INBOUND_WHITELIST = ["203.0.113.195"]
    FIRETEXT_INBOUND_SMS_AUTH = ["testkey"]
    TEMPLATE_PREVIEW_API_HOST = "http://localhost:9999"

    MMG_URL = "https://example.com/mmg"
    FIRETEXT_URL = "https://example.com/firetext"

    CBC_PROXY_ENABLED = True
    DVLA_EMAIL_ADDRESSES = ["success@simulator.amazonses.com", "success+2@simulator.amazonses.com"]

    DVLA_API_BASE_URL = "https://test-dvla-api.com"

    REGISTER_FUNCTIONAL_TESTING_BLUEPRINT = True

    SEND_LETTERS_ENABLED = True

    SEND_ZENDESK_ALERTS_ENABLED = True


class CloudFoundryConfig(Config):
    pass


# CloudFoundry sandbox
class Sandbox(CloudFoundryConfig):
    NOTIFY_EMAIL_DOMAIN = "notify.works"
    NOTIFY_ENVIRONMENT = "sandbox"
    S3_BUCKET_CSV_UPLOAD = "cf-sandbox-notifications-csv-upload"
    S3_BUCKET_CONTACT_LIST = "cf-sandbox-contact-list"
    S3_BUCKET_LETTERS_PDF = "cf-sandbox-letters-pdf"
    S3_BUCKET_TEST_LETTERS = "cf-sandbox-test-letters"
    S3_BUCKET_LETTERS_SCAN = "cf-sandbox-letters-scan"
    S3_BUCKET_INVALID_PDF = "cf-sandbox-letters-invalid-pdf"
    FROM_NUMBER = "sandbox"


configs = {
    "development": Development,
    "test": Test,
    "sandbox": Sandbox,
}
