import json

from requests import RequestException, request

from app.clients.sms import SmsClient, SmsClientResponseException

mmg_response_map = {
    "2": {
        "status": "permanent-failure",
        "substatus": {
            "1": "Number does not exist",
            "4": "Rejected by operator",
            "5": "Unidentified Subscriber",
            "9": "Undelivered",
            "11": "Service for Subscriber suspended",
            "12": "Illegal equipment",
            "2049": "Subscriber IMSI blacklisted",
            "2050": "Number blacklisted in do-not-disturb blacklist",
            "2052": "Destination number blacklisted",
            "2053": "Source address blacklisted",
        },
    },
    "3": {"status": "delivered", "substatus": {"2": "Delivered to operator", "5": "Delivered to handset"}},
    "4": {
        "status": "temporary-failure",
        "substatus": {
            "6": "Absent Subscriber",
            "8": "Roaming not allowed",
            "13": "SMS Not Supported",
            "15": "Expired",
            "27": "Absent Subscriber",
            "29": "Invalid delivery report",
            "32": "Delivery Failure",
        },
    },
    "5": {
        "status": "permanent-failure",
        "substatus": {
            "6": "Network out of coverage",
            "8": "Incorrect number prefix",
            "10": "Number on do-not-disturb service",
            "11": "Sender id not registered",
            "13": "Sender id blacklisted",
            "14": "Destination number blacklisted",
            "19": "Routing unavailable",
            "20": "Rejected by anti-flooding mechanism",
            "21": "System error",  # it says to retry those messages or contact support
            "23": "Duplicate message id",
            "24": "Message formatted incorrectly",
            "25": "Message too long",
            "51": "Missing recipient value",
            "52": "Invalid destination",
        },
    },
}


def get_mmg_responses(status, detailed_status_code=None):
    return (mmg_response_map[status]["status"], mmg_response_map[status]["substatus"].get(detailed_status_code, None))


class MMGClientResponseException(SmsClientResponseException):
    def __init__(self, response, exception):
        status_code = response.status_code if response is not None else 504
        text = response.text if response is not None else "Gateway Time-out"

        self.status_code = status_code
        self.text = text
        self.exception = exception

    def __str__(self):
        return "Code {} text {} exception {}".format(self.status_code, self.text, str(self.exception))


class MMGClient(SmsClient):
    """
    MMG sms client
    """

    def init_app(self, *args, **kwargs):
        super().init_app(*args, **kwargs)
        self.api_key = self.current_app.config.get("MMG_API_KEY")
        self.mmg_url = self.current_app.config.get("MMG_URL")

    @property
    def name(self):
        return "mmg"

    def try_send_sms(self, to, content, reference, international, sender):
        data = {"reqType": "BULK", "MSISDN": to, "msg": content, "sender": sender, "cid": reference, "multi": True}

        try:
            response = request(
                "POST",
                self.mmg_url,
                data=json.dumps(data),
                headers={"Content-Type": "application/json", "Authorization": "Basic {}".format(self.api_key)},
                timeout=60,
            )

            response.raise_for_status()
            try:
                json.loads(response.text)
            except (ValueError, AttributeError):
                raise SmsClientResponseException("Invalid response JSON")
        except RequestException:
            raise SmsClientResponseException("Request failed")

        return response
