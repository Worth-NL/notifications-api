import json
import os
from datetime import timedelta

from celery.schedules import crontab
from kombu import Exchange, Queue


class QueueNames(object):
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
    ANTIVIRUS = "antivirus-tasks"
    SANITISE_LETTERS = "sanitise-letter-tasks"
    SAVE_API_EMAIL = "save-api-email-tasks"
    SAVE_API_SMS = "save-api-sms-tasks"
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
            QueueNames.SAVE_API_EMAIL,
            QueueNames.SAVE_API_SMS,
            QueueNames.BROADCASTS,
        ]


class BroadcastProvider:
    EE = "ee"
    VODAFONE = "vodafone"
    THREE = "three"
    O2 = "o2"

    PROVIDERS = [EE, VODAFONE, THREE, O2]


class TaskNames(object):
    PROCESS_INCOMPLETE_JOBS = "process-incomplete-jobs"
    ZIP_AND_SEND_LETTER_PDFS = "zip-and-send-letter-pdfs"
    SCAN_FILE = "scan-file"
    SANITISE_LETTER = "sanitise-and-upload-letter"
    CREATE_PDF_FOR_TEMPLATED_LETTER = "create-pdf-for-templated-letter"
    PUBLISH_GOVUK_ALERTS = "publish-govuk-alerts"
    RECREATE_PDF_FOR_PRECOMPILED_LETTER = "recreate-pdf-for-precompiled-letter"


class Config(object):
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

    # Firetext API Key
    FIRETEXT_API_KEY = os.getenv("FIRETEXT_API_KEY")
    FIRETEXT_INTERNATIONAL_API_KEY = os.getenv("FIRETEXT_INTERNATIONAL_API_KEY", "placeholder")

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
    NOTIFY_LOG_PATH = os.getenv("NOTIFY_LOG_PATH")

    NOTIFY_RUNTIME_PLATFORM = os.getenv("NOTIFY_RUNTIME_PLATFORM", "paas")
    NOTIFY_REQUEST_LOG_LEVEL = os.getenv("NOTIFY_REQUEST_LOG_LEVEL", "INFO")

    # Cronitor
    CRONITOR_ENABLED = False
    CRONITOR_KEYS = json.loads(os.environ.get("CRONITOR_KEYS", "{}"))

    # Antivirus
    ANTIVIRUS_ENABLED = True

    ###########################
    # Default config values ###
    ###########################

    NOTIFY_ENVIRONMENT = "development"
    AWS_REGION = "eu-west-1"
    INVITATION_EXPIRATION_DAYS = 2
    NOTIFY_APP_NAME = "api"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(os.environ.get("SQLALCHEMY_POOL_SIZE", 5)),
        "pool_timeout": 30,
        "pool_recycle": 300,
        "connect_args": {
            "options": "-c statement_timeout=1200000",
        },
    }
    PAGE_SIZE = 50
    API_PAGE_SIZE = 250
    TEST_MESSAGE_FILENAME = "Test message"
    ONE_OFF_MESSAGE_FILENAME = "Report"
    MAX_VERIFY_CODE_COUNT = 5
    MAX_FAILED_LOGIN_COUNT = 10

    CHECK_PROXY_HEADER = False

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
    GO_LIVE_NEW_REQUEST_FOR_ORG_USERS_TEMPLATE_ID = "5c7cfc0f-c3f4-4bd6-9a84-5a144aad5425"
    GO_LIVE_REQUEST_NEXT_STEPS_FOR_ORG_USER_TEMPLATE_ID = "62f12a62-742b-4458-9336-741521b131c7"
    GO_LIVE_REQUEST_REJECTED_BY_ORG_USER_TEMPLATE_ID = "507d0796-9e23-4ad7-b83b-5efbd9496866"
    NOTIFY_INTERNATIONAL_SMS_SENDER = "07984404008"
    LETTERS_VOLUME_EMAIL_TEMPLATE_ID = "11fad854-fd38-4a7c-bd17-805fb13dfc12"
    NHS_EMAIL_BRANDING_ID = "a7dc4e56-660b-4db7-8cff-12c37b12b5ea"
    NHS_LETTER_BRANDING_ID = "2cd354bb-6b85-eda3-c0ad-6b613150459f"
    REQUEST_INVITE_TO_SERVICE_TEMPLATE_ID = "77677459-f862-44ee-96d9-b8cb2323d407"
    RECEIPT_FOR_REQUEST_INVITE_TO_SERVICE_TEMPLATE_ID = "38bcd263-6ce8-431f-979d-8e637c1f0576"
    # we only need real email in Live environment (production)
    DVLA_EMAIL_ADDRESSES = json.loads(os.environ.get("DVLA_EMAIL_ADDRESSES", "[]"))

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
            "check-if-letters-still-pending-virus-check": {
                "task": "check-if-letters-still-pending-virus-check",
                "schedule": crontab(minute="*/10"),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "check-for-services-with-high-failure-rates-or-sending-to-tv-numbers": {
                "task": "check-for-services-with-high-failure-rates-or-sending-to-tv-numbers",
                "schedule": crontab(day_of_week="mon-fri", hour=10, minute=30),
                "options": {"queue": QueueNames.PERIODIC},
            },
            "raise-alert-if-letter-notifications-still-sending": {
                "task": "raise-alert-if-letter-notifications-still-sending",
                "schedule": crontab(hour=17, minute=00),
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
            "raise-alert-if-no-letter-ack-file": {
                "task": "raise-alert-if-no-letter-ack-file",
                "schedule": crontab(hour=22, minute=45),
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

    FROM_NUMBER = "NOTIFYNL"

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
    ROUTE_SECRET_KEY_1 = os.environ.get("ROUTE_SECRET_KEY_1", "")
    ROUTE_SECRET_KEY_2 = os.environ.get("ROUTE_SECRET_KEY_2", "")

    HIGH_VOLUME_SERVICE = json.loads(os.environ.get("HIGH_VOLUME_SERVICE", "[]"))

    TEMPLATE_PREVIEW_API_HOST = os.environ.get("TEMPLATE_PREVIEW_API_HOST", "http://localhost:6013")
    TEMPLATE_PREVIEW_API_KEY = os.environ.get("TEMPLATE_PREVIEW_API_KEY", "my-secret-key")

    DOCUMENT_DOWNLOAD_API_HOST = os.environ.get("DOCUMENT_DOWNLOAD_API_HOST", "http://localhost:7000")
    DOCUMENT_DOWNLOAD_API_HOST_INTERNAL = os.environ.get("DOCUMENT_DOWNLOAD_API_HOST_INTERNAL", "http://localhost:7000")
    DOCUMENT_DOWNLOAD_API_KEY = os.environ.get("DOCUMENT_DOWNLOAD_API_KEY", "auth-token")

    # these environment vars aren't defined in the manifest so to set them on paas use `cf set-env`
    MMG_URL = os.environ.get("MMG_URL", "https://api.mmg.co.uk/jsonv2a/api.php")
    FIRETEXT_URL = os.environ.get("FIRETEXT_URL", "https://www.firetext.co.uk/api/sendsms/json")
    SPRYNG_URL = os.environ.get("SPRYNG_URL", "https://rest.spryngsms.com/v1/messages")
    SES_STUB_URL = os.environ.get("SES_STUB_URL")

    AWS_REGION = "eu-west-1"

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


######################
# Config overrides ###
######################
class Development(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False

    SERVER_NAME = os.getenv("SERVER_NAME")

    REDIS_ENABLED = os.getenv("REDIS_ENABLED") == "1"

    S3_BUCKET_CSV_UPLOAD = os.getenv("S3_BUCKET_CSV_UPLOAD", "notifynl-dev-notifications-csv-upload")
    S3_BUCKET_CONTACT_LIST = os.getenv("S3_BUCKET_CONTACT_LIST", "notifynl-dev-contact-list")
    S3_BUCKET_TEST_LETTERS = os.getenv("S3_BUCKET_TEST_LETTERS", "notifynl-dev-test-letters")
    S3_BUCKET_DVLA_RESPONSE = os.getenv("S3_BUCKET_DVLA_RESPONSE", "notifynl-dev-tools-ftp")
    S3_BUCKET_LETTERS_PDF = os.getenv("S3_BUCKET_LETTERS_PDF", "notifynl-dev-letters-pdf")
    S3_BUCKET_LETTERS_SCAN = os.getenv("S3_BUCKET_LETTERS_SCAN", "notifynl-dev-letters-scan")
    S3_BUCKET_INVALID_PDF = os.getenv("S3_BUCKET_INVALID_PDF", "notifynl-dev-letters-invalid-pdf")
    S3_BUCKET_TRANSIENT_UPLOADED_LETTERS = os.getenv(
        "S3_BUCKET_TRANSIENT_UPLOADED_LETTERS", "notifynl-dev-transient-uploaded-letters"
    )
    S3_BUCKET_LETTER_SANITISE = os.getenv("S3_BUCKET_LETTER_SANITISE", "notifynl-dev-letters-sanitise")

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
    NOTIFY_LOG_PATH = "application.log"
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


class Test(Development):
    NOTIFY_EMAIL_DOMAIN = "test.notifynl.nl"
    FROM_NUMBER = "NOTIFYNLTEST"
    NOTIFY_ENVIRONMENT = "test"
    TESTING = True

    HIGH_VOLUME_SERVICE = [
        "941b6f9a-50d7-4742-8d50-f365ca74bf27",
        "63f95b86-2d19-4497-b8b2-ccf25457df4e",
        "7e5950cb-9954-41f5-8376-962b8c8555cf",
        "10d1b9c9-0072-4fa9-ae1c-595e333841da",
    ]

    S3_BUCKET_CSV_UPLOAD = "notifynl-test-csv-upload"
    S3_BUCKET_CONTACT_LIST = "notifynl-test-contact-list"
    S3_BUCKET_TEST_LETTERS = "notifynl-test-test-letters"
    S3_BUCKET_DVLA_RESPONSE = "notifynl-test-tools-ftp"
    S3_BUCKET_LETTERS_PDF = "notifynl-test-letters-pdf"
    S3_BUCKET_LETTERS_SCAN = "notifynl-test-letters-scan"
    S3_BUCKET_INVALID_PDF = "notifynl-test-letters-invalid-pdf"
    S3_BUCKET_TRANSIENT_UPLOADED_LETTERS = "notifynl-test-transient-uploaded-letters"
    S3_BUCKET_LETTER_SANITISE = "notifynl-test-letters-sanitise"

    # when testing, the SQLALCHEMY_DATABASE_URI is used for the postgres server's location
    # but the database name is set in the _notify_db fixture
    SQLALCHEMY_RECORD_QUERIES = True

    CELERY = {**Config.CELERY, "broker_url": "you-forgot-to-mock-celery-in-your-tests://"}

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


class Preview(Config):
    NOTIFY_EMAIL_DOMAIN = "notify.works"
    NOTIFY_ENVIRONMENT = "preview"
    S3_BUCKET_CSV_UPLOAD = "preview-notifications-csv-upload"
    S3_BUCKET_CONTACT_LIST = "preview-contact-list"
    S3_BUCKET_TEST_LETTERS = "preview-test-letters"
    S3_BUCKET_DVLA_RESPONSE = "notify.works-ftp"
    S3_BUCKET_LETTERS_PDF = "preview-letters-pdf"
    S3_BUCKET_LETTERS_SCAN = "preview-letters-scan"
    S3_BUCKET_INVALID_PDF = "preview-letters-invalid-pdf"
    S3_BUCKET_TRANSIENT_UPLOADED_LETTERS = "preview-transient-uploaded-letters"
    S3_BUCKET_LETTER_SANITISE = "preview-letters-sanitise"
    FROM_NUMBER = "preview"
    API_RATE_LIMIT_ENABLED = True
    CHECK_PROXY_HEADER = False
    DVLA_API_TLS_CIPHERS = os.environ.get("DVLA_API_TLS_CIPHERS", "must-supply-tls-ciphers")


class Staging(Config):
    NOTIFY_EMAIL_DOMAIN = "acc.notifynl.nl"
    NOTIFY_ENVIRONMENT = "staging"
    S3_BUCKET_CSV_UPLOAD = "notifynl-acc-csv-upload"
    S3_BUCKET_CONTACT_LIST = "notifynl-acc-contact-list"
    S3_BUCKET_TEST_LETTERS = "notifynl-acc-test-letters"
    S3_BUCKET_DVLA_RESPONSE = "notifynl-acc-tools-ftp"
    S3_BUCKET_LETTERS_PDF = "notifynl-acc-letters-pdf"
    S3_BUCKET_LETTERS_SCAN = "notifynl-acc-letters-scan"
    S3_BUCKET_INVALID_PDF = "notifynl-acc-letters-invalid-pdf"
    S3_BUCKET_TRANSIENT_UPLOADED_LETTERS = "notifynl-acc-transient-uploaded-letters"
    S3_BUCKET_LETTER_SANITISE = "notifynl-acc-letters-sanitise"
    FROM_NUMBER = "NOTIFYNLACC"
    API_RATE_LIMIT_ENABLED = True
    CHECK_PROXY_HEADER = False if os.environ.get("CHECK_PROXY_HEADER") == "0" else True
    DVLA_API_TLS_CIPHERS = os.environ.get("DVLA_API_TLS_CIPHERS", "must-supply-tls-ciphers")


class Production(Config):
    NOTIFY_EMAIL_DOMAIN = "notifynl.nl"
    NOTIFY_ENVIRONMENT = "production"
    S3_BUCKET_CSV_UPLOAD = "notifynl-prod-csv-upload"
    S3_BUCKET_CONTACT_LIST = "notifynl-prod-contact-list"
    S3_BUCKET_TEST_LETTERS = "notifynl-prod-test-letters"
    S3_BUCKET_DVLA_RESPONSE = "notifynl-prod-tools-ftp"
    S3_BUCKET_LETTERS_PDF = "notifynl-prod-letters-pdf"
    S3_BUCKET_LETTERS_SCAN = "notifynl-prod-letters-scan"
    S3_BUCKET_INVALID_PDF = "notifynl-prod-letters-invalid-pdf"
    S3_BUCKET_TRANSIENT_UPLOADED_LETTERS = "notifynl-prod-transient-uploaded-letters"
    S3_BUCKET_LETTER_SANITISE = "notifynl-prod-letters-sanitise"
    FROM_NUMBER = "NOTIFYNL"
    API_RATE_LIMIT_ENABLED = True
    CHECK_PROXY_HEADER = False if os.environ.get("CHECK_PROXY_HEADER") == "0" else True
    SES_STUB_URL = None

    CRONITOR_ENABLED = True

    DVLA_API_BASE_URL = os.environ.get("DVLA_API_BASE_URL", "https://driver-vehicle-licensing.api.gov.uk")
    DVLA_API_TLS_CIPHERS = os.environ.get("DVLA_API_TLS_CIPHERS", "must-supply-tls-ciphers")


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
    S3_BUCKET_DVLA_RESPONSE = "notify.works-ftp"
    S3_BUCKET_LETTERS_SCAN = "cf-sandbox-letters-scan"
    S3_BUCKET_INVALID_PDF = "cf-sandbox-letters-invalid-pdf"
    FROM_NUMBER = "sandbox"


configs = {
    "development": Development,
    "test": Test,
    "production": Production,
    "staging": Staging,
    "preview": Preview,
    "sandbox": Sandbox,
}
