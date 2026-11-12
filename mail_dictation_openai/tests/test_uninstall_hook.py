# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import sys

from odoo.modules.module import get_manifest
from odoo.tests import TransactionCase

from ..hooks import uninstall_hook

KEYS = [
    "mail_dictation.address",
    "mail_dictation.api_key",
    "mail_dictation.model",
    "mail_dictation.provider",
    "mailXdictation.address",
]


class TestUninstallHook(TransactionCase):
    def remaining_keys(self):
        return (
            self.env["ir.config_parameter"].search([("key", "in", KEYS)]).mapped("key")
        )

    def test_uninstall_deletes_its_settings_and_its_choice(self):
        params = self.env["ir.config_parameter"]
        params.set_param("mail_dictation.address", "https://gateway.example.com/v1")
        params.set_param("mail_dictation.api_key", "fake-dictation-key")
        params.set_param("mail_dictation.model", "whisper-1")
        params.set_param("mail_dictation.provider", "openai")
        # «_» matches any character in a LIKE pattern.
        params.set_param("mailXdictation.address", "an unrelated value")

        uninstall_hook(self.env.cr, self.env.registry)

        self.assertEqual(self.remaining_keys(), ["mailXdictation.address"])

    def test_uninstall_keeps_the_choice_of_another_service(self):
        self.env["ir.config_parameter"].set_param("mail_dictation.provider", "other")

        uninstall_hook(self.env.cr, self.env.registry)

        self.assertEqual(self.remaining_keys(), ["mail_dictation.provider"])

    def test_odoo_runs_the_hook_on_uninstall(self):
        # Odoo calls the function the manifest names on the module's package
        # (odoo/modules/loading.py, load_modules).
        hook_name = get_manifest("mail_dictation_openai")["uninstall_hook"]
        package = sys.modules["odoo.addons.mail_dictation_openai"]
        self.assertIs(getattr(package, hook_name), uninstall_hook)
