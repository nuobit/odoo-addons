# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestQunit(HttpCase):
    def test_qunit(self):
        self.browser_js(
            "/web/tests?module=mail_app_icon_flat&failfast",
            "",
            "",
            login="admin",
        )
