# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import json

import requests

# The messages the user reads, as the server words them in English.
NOT_CONFIGURED = (
    "Dictation is not configured: an administrator must enter the "
    "transcription service key in Settings > Discuss."
)
UNREACHABLE = "The transcription service could not be reached. Try again in a moment."
KEY_REFUSED = (
    "The transcription service refused the key: an administrator must check "
    "it in Settings > Discuss."
)
QUOTA_USED_UP = (
    "The dictation quota is used up: an administrator must add credit or "
    "raise the spending limit at the transcription service."
)
BUSY = "The transcription service is busy. Try again in a moment."
FAILED = "The transcription service failed. Try again in a moment."


def service_response(status, payload):
    """Return the transcription service's answer, with a JSON body."""
    response = requests.Response()
    response.status_code = status
    response.headers["Content-Type"] = "application/json"
    response._content = json.dumps(payload).encode()
    return response


def service_error(status, code):
    """Return an error of the OpenAI API, in the shape the API answers it."""
    return service_response(
        status,
        {
            "error": {
                "message": "The provider's own explanation.",
                "type": "requests",
                "param": None,
                "code": code,
            }
        },
    )


def page_response(status):
    """Return an HTML page, as a proxy or a gateway answers an error."""
    response = requests.Response()
    response.status_code = status
    response.headers["Content-Type"] = "text/html"
    response._content = b"<html><body>Bad Gateway</body></html>"
    return response
