# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import sys

from odoo.modules.module import get_manifest
from odoo.tests import TransactionCase

from ..hooks import uninstall_hook


class TestUninstallHook(TransactionCase):
    def test_uninstall_deletes_the_choice_of_service_only(self):
        params = self.env["ir.config_parameter"]
        params.set_param("mail_dictation.provider", "openai")
        # «_» matches any character in a LIKE pattern.
        params.set_param("mailXdictation.provider", "an unrelated value")

        uninstall_hook(self.env.cr, self.env.registry)

        self.assertEqual(
            params.search(
                [("key", "in", ["mail_dictation.provider", "mailXdictation.provider"])]
            ).mapped("key"),
            ["mailXdictation.provider"],
        )

    def test_odoo_runs_the_hook_on_uninstall(self):
        # Odoo calls the function the manifest names on the module's package
        # (odoo/modules/loading.py, load_modules).
        hook_name = get_manifest("mail_dictation")["uninstall_hook"]
        package = sys.modules["odoo.addons.mail_dictation"]
        self.assertIs(getattr(package, hook_name), uninstall_hook)
