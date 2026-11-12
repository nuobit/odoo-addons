# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from unittest import mock

from odoo_test_helper import FakeModelLoader

from odoo.exceptions import UserError
from odoo.tests import TransactionCase

from .common import NOT_CONFIGURED

AUDIO = b"fake-audio-of-a-sentence"


class TestMailDictation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .fake_models import MailDictationFake

        cls.loader.update_registry((MailDictationFake,))

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def transcribe(self):
        return self.env["mail.dictation"]._transcribe(
            AUDIO, "dictation.webm", "audio/webm"
        )

    def fake_service_answers(self, text):
        """Patch the fake service to answer ``text``."""
        return mock.patch.object(
            type(self.env["mail.dictation.fake"]), "_transcribe", return_value=text
        )

    def test_the_chosen_service_transcribes(self):
        self.env["ir.config_parameter"].set_param("mail_dictation.provider", "fake")
        with self.fake_service_answers("Bon dia") as service:
            text = self.transcribe()
        self.assertEqual(text, "Bon dia")
        service.assert_called_once_with(AUDIO, "dictation.webm", "audio/webm")

    def test_the_text_comes_without_the_whitespace_around_it(self):
        self.env["ir.config_parameter"].set_param("mail_dictation.provider", "fake")
        with self.fake_service_answers(" Bon dia \n"):
            text = self.transcribe()
        self.assertEqual(text, "Bon dia")

    def test_whitespace_only_is_an_empty_text(self):
        self.env["ir.config_parameter"].set_param("mail_dictation.provider", "fake")
        with self.fake_service_answers("  \n"):
            text = self.transcribe()
        self.assertEqual(text, "")

    def test_no_service_is_not_configured(self):
        with self.fake_service_answers("Bon dia") as service:
            with self.assertRaises(UserError) as error:
                self.transcribe()
        self.assertEqual(error.exception.args[0], NOT_CONFIGURED)
        service.assert_not_called()

    def test_a_service_no_module_defines_is_not_configured(self):
        # The chosen service's module was uninstalled.
        self.env["ir.config_parameter"].set_param("mail_dictation.provider", "gone")
        with self.fake_service_answers("Bon dia") as service:
            with self.assertRaises(UserError) as error:
                self.transcribe()
        self.assertEqual(error.exception.args[0], NOT_CONFIGURED)
        service.assert_not_called()
