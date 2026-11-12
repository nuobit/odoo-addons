# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging
from unittest import mock

import requests

from odoo.exceptions import UserError
from odoo.tests import TransactionCase

from .common import (
    BUSY,
    FAILED,
    KEY_REFUSED,
    NOT_CONFIGURED,
    QUOTA_USED_UP,
    UNREACHABLE,
    page_response,
    service_error,
    service_response,
)

AUDIO = b"fake-audio-of-a-sentence"
TEXT = "Hola, això és una prova de dictat."
LOGGER = "odoo.addons.mail_dictation_openai.models.mail_dictation_openai"


class TestMailDictationOpenai(TransactionCase):
    def setUp(self):
        super().setUp()
        params = self.env["ir.config_parameter"]
        params.set_param("mail_dictation.provider", "openai")
        params.set_param("mail_dictation.api_key", "fake-dictation-key")

    def transcribe(self):
        # Through mail_dictation's entry, as the route calls it.
        return self.env["mail.dictation"]._transcribe(
            AUDIO, "dictation.webm", "audio/webm"
        )

    def assertTranscriptionFails(self, message, **post):
        """Assert that the service's answer reaches the user as ``message`` and
        is logged; ``post`` is how the faked ``requests.post`` answers."""
        with mock.patch.object(requests, "post", **post):
            with self.assertLogs(LOGGER, logging.WARNING):
                with self.assertRaises(UserError) as error:
                    self.transcribe()
        self.assertEqual(error.exception.args[0], message)

    def test_success_returns_the_text_and_sends_no_language(self):
        with mock.patch.object(
            requests, "post", return_value=service_response(200, {"text": TEXT})
        ) as post:
            text = self.transcribe()
        self.assertEqual(text, TEXT)
        post.assert_called_once_with(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": "Bearer fake-dictation-key"},
            data={"model": "gpt-transcribe"},
            files={"file": ("dictation.webm", AUDIO, "audio/webm")},
            timeout=60,
        )

    def test_success_uses_the_configured_address_and_model(self):
        params = self.env["ir.config_parameter"]
        params.set_param("mail_dictation.address", "https://gateway.example.com/v1/")
        params.set_param("mail_dictation.model", "whisper-1")
        with mock.patch.object(
            requests, "post", return_value=service_response(200, {"text": TEXT})
        ) as post:
            self.transcribe()
        self.assertEqual(
            post.call_args.args,
            ("https://gateway.example.com/v1/audio/transcriptions",),
        )
        self.assertEqual(post.call_args.kwargs["data"], {"model": "whisper-1"})

    def test_success_with_no_words_returns_an_empty_text(self):
        with mock.patch.object(
            requests, "post", return_value=service_response(200, {"text": ""})
        ):
            text = self.transcribe()
        self.assertEqual(text, "")

    def test_success_strips_the_text(self):
        with mock.patch.object(
            requests,
            "post",
            return_value=service_response(200, {"text": " Bon dia \n"}),
        ):
            text = self.transcribe()
        self.assertEqual(text, "Bon dia")

    def test_success_with_only_whitespace_returns_an_empty_text(self):
        with mock.patch.object(
            requests, "post", return_value=service_response(200, {"text": "  \n"})
        ):
            text = self.transcribe()
        self.assertEqual(text, "")

    def test_no_key_is_not_configured(self):
        self.env["ir.config_parameter"].set_param("mail_dictation.api_key", False)
        with mock.patch.object(requests, "post") as post:
            with self.assertRaises(UserError) as error:
                self.transcribe()
        self.assertEqual(error.exception.args[0], NOT_CONFIGURED)
        post.assert_not_called()

    def test_service_unreachable(self):
        self.assertTranscriptionFails(UNREACHABLE, side_effect=requests.ConnectionError)

    def test_service_timeout(self):
        self.assertTranscriptionFails(UNREACHABLE, side_effect=requests.Timeout)

    def test_key_refused_401(self):
        self.assertTranscriptionFails(
            KEY_REFUSED, return_value=service_error(401, "invalid_api_key")
        )

    def test_key_refused_403(self):
        self.assertTranscriptionFails(
            KEY_REFUSED,
            return_value=service_error(403, "unsupported_country_region_territory"),
        )

    def test_quota_project_spend_limit_exceeded(self):
        self.assertTranscriptionFails(
            QUOTA_USED_UP,
            return_value=service_error(429, "project_spend_limit_exceeded"),
        )

    def test_quota_organization_spend_limit_exceeded(self):
        self.assertTranscriptionFails(
            QUOTA_USED_UP,
            return_value=service_error(429, "organization_spend_limit_exceeded"),
        )

    def test_quota_credit_balance_exhausted(self):
        self.assertTranscriptionFails(
            QUOTA_USED_UP, return_value=service_error(429, "credit_balance_exhausted")
        )

    def test_quota_insufficient_quota(self):
        self.assertTranscriptionFails(
            QUOTA_USED_UP, return_value=service_error(429, "insufficient_quota")
        )

    def test_other_429_is_busy(self):
        self.assertTranscriptionFails(
            BUSY, return_value=service_error(429, "rate_limit_exceeded")
        )

    def test_429_with_a_null_code_is_busy(self):
        self.assertTranscriptionFails(BUSY, return_value=service_error(429, None))

    def test_429_with_a_code_that_is_not_text_is_busy(self):
        self.assertTranscriptionFails(
            BUSY, return_value=service_error(429, ["insufficient_quota"])
        )

    def test_429_without_json_is_busy(self):
        self.assertTranscriptionFails(BUSY, return_value=page_response(429))

    def test_other_error_status_failed(self):
        self.assertTranscriptionFails(
            FAILED, return_value=service_error(400, "invalid_value")
        )

    def test_server_error_page_failed(self):
        self.assertTranscriptionFails(FAILED, return_value=page_response(502))

    def test_answer_without_a_text_failed(self):
        self.assertTranscriptionFails(
            FAILED, return_value=service_response(200, {"task": "transcribe"})
        )

    def test_neither_the_audio_nor_the_text_nor_the_key_is_logged(self):
        with self.assertLogs(LOGGER, logging.DEBUG) as logs:
            with mock.patch.object(
                requests, "post", return_value=service_response(200, {"text": TEXT})
            ):
                self.transcribe()
            with mock.patch.object(
                requests,
                "post",
                return_value=service_response(
                    401,
                    {
                        "error": {
                            "message": "Incorrect API key provided: fake-dictation-key.",
                            "code": "invalid_api_key",
                        }
                    },
                ),
            ):
                with self.assertRaises(UserError):
                    self.transcribe()
        self.assertEqual(len(logs.output), 2)
        for line in logs.output:
            self.assertNotIn(TEXT, line)
            self.assertNotIn(AUDIO.decode(), line)
            self.assertNotIn("fake-dictation-key", line)

    def test_settings_default_to_the_standard_service(self):
        self.env["ir.config_parameter"].search(
            [("key", "in", ("mail_dictation.address", "mail_dictation.model"))]
        ).unlink()
        # The values the Settings page opens with.
        defaults = self.env["res.config.settings"].default_get(
            ["mail_dictation_address", "mail_dictation_api_key", "mail_dictation_model"]
        )
        self.assertEqual(
            defaults["mail_dictation_address"], "https://api.openai.com/v1"
        )
        self.assertEqual(defaults["mail_dictation_api_key"], "fake-dictation-key")
        self.assertEqual(defaults["mail_dictation_model"], "gpt-transcribe")
