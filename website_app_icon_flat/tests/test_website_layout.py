# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from lxml import html

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteLayout(HttpCase):
    def test_editor_button_shows_flat_icon(self):
        self.authenticate("admin", "admin")
        # Not the home page: website_erp_login, installed with every other
        # addon of this repository on its CI, reroutes it to the backend.
        page = html.fromstring(self.url_open("/website/info").content)
        [icon] = page.xpath(
            "//a[contains(concat(' ', @class, ' '), ' o_frontend_to_backend_edit_btn ')]"
            "/img"
        )
        flat_icon_urls = self.env["ir.module.module"]._get_flat_icon_urls()
        self.assertEqual(
            icon.get("src"), flat_icon_urls["/website/static/description/icon.png"]
        )
