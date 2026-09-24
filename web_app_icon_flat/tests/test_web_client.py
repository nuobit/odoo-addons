# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import base64
import json

from odoo.tests import HttpCase, tagged

from .test_ir_module_module import read_module_file


@tagged("post_install", "-at_install")
class TestWebClient(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings_app = cls.env.ref("base.menu_administration")
        users_action = cls.env.ref("base.action_res_users")
        cls.other_app = cls.env["ir.ui.menu"].create(
            {
                "name": "Other App",
                "web_icon": "web_app_icon_flat,static/description/icon.png",
                "action": f"{users_action._name},{users_action.id}",
            }
        )

    def load_web_menus(self):
        self.authenticate("admin", "admin")
        return self.url_open("/web/webclient/load_menus/test").json()

    def test_odoo_app_menu_shows_flat_icon(self):
        menus = self.load_web_menus()
        self.assertEqual(
            base64.b64decode(menus[str(self.settings_app.id)]["webIconData"]),
            read_module_file("web_app_icon_flat", "static/img/base/settings.png"),
        )

    def test_other_app_menu_keeps_its_icon(self):
        menus = self.load_web_menus()
        self.assertEqual(
            base64.b64decode(menus[str(self.other_app.id)]["webIconData"]),
            read_module_file("web_app_icon_flat", "static/description/icon.png"),
        )

    def test_stored_menu_icon_unchanged(self):
        self.load_web_menus()
        self.assertEqual(
            self.settings_app.web_icon, "base,static/description/settings.png"
        )
        self.assertEqual(
            base64.b64decode(self.settings_app.web_icon_data),
            read_module_file("base", "static/description/settings.png"),
        )

    def test_session_info_lists_flat_icons(self):
        self.authenticate("admin", "admin")
        session_info = self.url_open(
            "/web/session/get_session_info",
            data=json.dumps({"jsonrpc": "2.0", "method": "call", "params": {}}),
            headers={"Content-Type": "application/json"},
        ).json()["result"]
        flat_icon_urls = session_info["flat_icon_urls"]
        self.assertEqual(
            flat_icon_urls["/base/static/description/settings.png"],
            "/web_app_icon_flat/static/img/base/settings.png",
        )
        self.assertEqual(
            flat_icon_urls["/crm/static/description/icon.png"],
            "/web_app_icon_flat/static/img/crm/icon.png",
        )
        self.assertNotIn(
            "/web_app_icon_flat/static/description/icon.png", flat_icon_urls
        )
