# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import xmlrpc.client
from unittest import mock

import requests

from odoo import http
from odoo.tests import HttpCase, get_db_name, new_test_user, tagged
from odoo.tools import mute_logger

from .common import service_response

AUDIO = b"fake-audio-of-a-sentence"


@tagged("post_install", "-at_install")
class TestMailDictationOpenaiRoute(HttpCase):
    def setUp(self):
        super().setUp()
        params = self.env["ir.config_parameter"]
        params.set_param("mail_dictation.provider", "openai")
        params.set_param("mail_dictation.api_key", "fake-dictation-key")
        self.internal_user = new_test_user(
            self.env, login="dictation_internal_test", groups="base.group_user"
        )

    def test_whitespace_only_text_is_an_empty_text(self):
        self.authenticate("dictation_internal_test", "dictation_internal_test")
        with mock.patch.object(
            requests, "post", return_value=service_response(200, {"text": "  \n"})
        ):
            response = self.url_open(
                "/mail_dictation/transcribe",
                data={"csrf_token": http.Request.csrf_token(self)},
                files={"audio": ("dictation.webm", AUDIO, "audio/webm")},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"text": ""})

    @mute_logger("odoo.http")
    def test_the_service_call_cannot_be_called_over_rpc(self):
        with mock.patch.object(requests, "post") as post:
            with self.assertRaises(xmlrpc.client.Fault) as error:
                self.xmlrpc_object.execute_kw(
                    get_db_name(),
                    self.internal_user.id,
                    "dictation_internal_test",
                    "mail.dictation.openai",
                    "_transcribe",
                    ["audio", "dictation.webm", "audio/webm"],
                )
        self.assertIn("Private methods", error.exception.faultString)
        post.assert_not_called()
