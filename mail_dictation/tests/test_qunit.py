# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests import HttpCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestQunit(HttpCase):
    def test_qunit(self):
        new_test_user(self.env, login="dictation_qunit_test", groups="base.group_user")
        self.browser_js(
            "/web/tests?module=mail_dictation&failfast",
            "",
            "",
            login="dictation_qunit_test",
        )
