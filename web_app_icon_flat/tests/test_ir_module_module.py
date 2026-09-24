# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import base64

from odoo.modules import get_module_resource
from odoo.tests import TransactionCase


def read_module_file(module, path):
    with open(get_module_resource(module, *path.split("/")), "rb") as file:
        return file.read()


class TestIrModuleModule(TransactionCase):
    def test_odoo_app_shows_flat_icon(self):
        # Every Odoo addon of the server has its record in the Apps list,
        # installed or not.
        crm = self.env.ref("base.module_crm")
        self.assertEqual(crm.display_icon, "/web_app_icon_flat/static/img/crm/icon.png")
        self.assertEqual(
            base64.b64decode(crm.icon_image),
            read_module_file("web_app_icon_flat", "static/img/crm/icon.png"),
        )

    def test_module_without_icon_shows_flat_default_icon(self):
        # bus has no icon of its own, so the Apps list shows the one of base.
        bus = self.env.ref("base.module_bus")
        self.assertEqual(
            bus.display_icon, "/web_app_icon_flat/static/img/base/icon.png"
        )
        self.assertEqual(
            base64.b64decode(bus.icon_image),
            read_module_file("web_app_icon_flat", "static/img/base/icon.png"),
        )

    def test_other_module_keeps_its_icon(self):
        module = self.env.ref("base.module_web_app_icon_flat")
        self.assertEqual(
            module.display_icon, "/web_app_icon_flat/static/description/icon.png"
        )
        self.assertEqual(
            base64.b64decode(module.icon_image),
            read_module_file("web_app_icon_flat", "static/description/icon.png"),
        )

    def test_stored_icon_unchanged(self):
        crm = self.env.ref("base.module_crm")
        self.assertEqual(crm.icon, "/crm/static/description/icon.png")
