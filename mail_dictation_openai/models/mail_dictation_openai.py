# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

import requests

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# This service's value in mail_dictation's choice of service, and so the
# suffix of the model mail_dictation sends the audio to.
SERVICE = "openai"

# The parameters that hold this service's settings (Settings > Discuss): the
# settings write them, the call reads them, and the uninstall hook deletes them.
ADDRESS_PARAM = "mail_dictation.address"
API_KEY_PARAM = "mail_dictation.api_key"
MODEL_PARAM = "mail_dictation.model"
SETTINGS_PARAMS = (ADDRESS_PARAM, API_KEY_PARAM, MODEL_PARAM)

# The standard values of the settings, which an administrator can change in
# Settings > Discuss.
DEFAULT_ADDRESS = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-transcribe"

# Seconds the server waits for the transcription service's answer.
TIMEOUT = 60

# The error codes of an HTTP 429 that mean the credit or the spending limit is
# used up (OpenAI API); any other 429 means the service is busy.
QUOTA_ERROR_CODES = frozenset(
    {
        "credit_balance_exhausted",
        "insufficient_quota",
        "organization_spend_limit_exceeded",
        "project_spend_limit_exceeded",
    }
)


class MailDictationOpenai(models.AbstractModel):
    _name = "mail.dictation.openai"
    _description = "Dictation through an OpenAI-compatible service"

    @api.model
    def _transcribe(self, audio, filename, mimetype):
        """Return the text the transcription service hears in ``audio``.

        It calls the OpenAI-compatible ``<address>/audio/transcriptions`` and
        sends no language: the service detects it. Every failure raises a
        ``UserError`` whose message is meant for the user. Neither the audio
        nor the text is logged or stored.

        Private, so that only ``mail.dictation._transcribe``, behind the route
        that refuses users who are not internal, can reach it: a public method
        could be called over RPC.
        """
        params = self.env["ir.config_parameter"].sudo()
        api_key = params.get_param(API_KEY_PARAM)
        if not api_key:
            raise UserError(
                _(
                    "Dictation is not configured: an administrator must enter "
                    "the transcription service key in Settings > Discuss."
                )
            )
        address = params.get_param(ADDRESS_PARAM, DEFAULT_ADDRESS)
        model = params.get_param(MODEL_PARAM, DEFAULT_MODEL)
        try:
            response = requests.post(
                f"{address.rstrip('/')}/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                data={"model": model},
                files={"file": (filename, audio, mimetype)},
                timeout=TIMEOUT,
            )
        except requests.RequestException as error:
            _logger.warning(
                "Dictation: the transcription service could not be reached "
                "(%s bytes of audio): %s",
                len(audio),
                error,
            )
            raise UserError(
                _(
                    "The transcription service could not be reached. "
                    "Try again in a moment."
                )
            ) from error
        if not response.ok:
            _logger.warning(
                "Dictation: the transcription service answered HTTP %s, "
                "error code %s (%s bytes of audio)",
                response.status_code,
                self._error_code(response),
                len(audio),
            )
            raise UserError(self._error_message(response))
        _logger.info(
            "Dictation: the transcription service answered HTTP %s "
            "(%s bytes of audio)",
            response.status_code,
            len(audio),
        )
        return self._response_text(response)

    @api.model
    def _error_message(self, response):
        """Return the user's message for an error status of the service."""
        status = response.status_code
        if status in (401, 403):
            message = _(
                "The transcription service refused the key: an administrator "
                "must check it in Settings > Discuss."
            )
        elif status == 429:
            if self._error_code(response) in QUOTA_ERROR_CODES:
                message = _(
                    "The dictation quota is used up: an administrator must "
                    "add credit or raise the spending limit at the "
                    "transcription service."
                )
            else:
                message = _("The transcription service is busy. Try again in a moment.")
        else:
            message = self._failure_message()
        return message

    @api.model
    def _error_code(self, response):
        """Return the ``error.code`` of the service's JSON answer, or None.

        A service that answers without one is legitimate: a gateway's or a
        proxy's error page carries no OpenAI error code, and OpenAI itself
        sends a null code with some errors.
        """
        try:
            code = response.json()["error"]["code"]
        except (ValueError, KeyError, TypeError):
            code = None
        return code if isinstance(code, str) else None

    @api.model
    def _response_text(self, response):
        """Return the ``text`` of a successful answer.

        An answer without a text (another program at the configured address,
        say) is the service failing.
        """
        try:
            text = response.json()["text"]
        except (ValueError, KeyError, TypeError):
            text = None
        if not isinstance(text, str):
            _logger.warning(
                "Dictation: the transcription service answered HTTP %s without "
                "a text",
                response.status_code,
            )
            raise UserError(self._failure_message())
        return text

    @api.model
    def _failure_message(self):
        return _("The transcription service failed. Try again in a moment.")
