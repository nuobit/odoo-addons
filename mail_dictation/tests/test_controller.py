# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import xmlrpc.client
from unittest import mock

from odoo import http
from odoo.tests import HttpCase, get_db_name, new_test_user, tagged
from odoo.tools import mute_logger

from .common import NOT_CONFIGURED

AUDIO = b"fake-audio-of-a-sentence"
TEXT = "Hola, això és una prova de dictat."


@tagged("post_install", "-at_install")
class TestMailDictationRoute(HttpCase):
    def setUp(self):
        super().setUp()
        self.internal_user = new_test_user(
            self.env, login="dictation_internal_test", groups="base.group_user"
        )
        new_test_user(
            self.env, login="dictation_portal_test", groups="base.group_portal"
        )

    def post_recording(self, login, files):
        self.authenticate(login, login)
        return self.url_open(
            "/mail_dictation/transcribe",
            data={"csrf_token": http.Request.csrf_token(self)},
            files=files,
        )

    def transcription(self, **answer):
        """Patch the transcription, which ``answer`` gives as ``mock.patch``
        arguments."""
        return mock.patch.object(
            type(self.env["mail.dictation"]), "_transcribe", **answer
        )

    def test_internal_user_gets_the_text(self):
        with self.transcription(return_value=TEXT) as transcribe:
            response = self.post_recording(
                "dictation_internal_test",
                {"audio": ("dictation.webm", AUDIO, "audio/webm")},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"text": TEXT})
        transcribe.assert_called_once_with(AUDIO, "dictation.webm", "audio/webm")

    def test_failure_returns_its_message(self):
        # No transcription service is chosen.
        response = self.post_recording(
            "dictation_internal_test",
            {"audio": ("dictation.webm", AUDIO, "audio/webm")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"error": NOT_CONFIGURED})

    def test_portal_user_is_refused(self):
        with self.transcription(return_value=TEXT) as transcribe:
            response = self.post_recording(
                "dictation_portal_test",
                {"audio": ("dictation.webm", AUDIO, "audio/webm")},
            )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"error": "Only internal users can dictate."})
        transcribe.assert_not_called()

    def test_oversized_recording_is_refused(self):
        with self.transcription(return_value=TEXT) as transcribe:
            response = self.post_recording(
                "dictation_internal_test",
                {
                    "audio": (
                        "dictation.webm",
                        b"x" * (25 * 1024 * 1024 + 1),
                        "audio/webm",
                    )
                },
            )
        self.assertEqual(response.status_code, 413)
        self.assertEqual(
            response.json(), {"error": "The recording is too long to be transcribed."}
        )
        transcribe.assert_not_called()

    def test_recording_at_the_bound_is_forwarded(self):
        with self.transcription(return_value=TEXT) as transcribe:
            response = self.post_recording(
                "dictation_internal_test",
                {"audio": ("dictation.webm", b"x" * (25 * 1024 * 1024), "audio/webm")},
            )
        self.assertEqual(response.status_code, 200)
        transcribe.assert_called_once()

    def test_request_without_a_recording_is_refused(self):
        with self.transcription(return_value=TEXT) as transcribe:
            response = self.post_recording("dictation_internal_test", None)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {"error": "The request carries no recording."}
        )
        transcribe.assert_not_called()

    @mute_logger("odoo.http")
    def test_transcribe_cannot_be_called_over_rpc(self):
        with self.assertRaises(xmlrpc.client.Fault) as error:
            self.xmlrpc_object.execute_kw(
                get_db_name(),
                self.internal_user.id,
                "dictation_internal_test",
                "mail.dictation",
                "_transcribe",
                ["audio", "dictation.webm", "audio/webm"],
            )
        self.assertIn("Private methods", error.exception.faultString)
