# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import WooCommerceCase


class TestPartnerBinding(WooCommerceCase):
    def test_address_the_import_creates_gives_its_parent_no_address(self):
        customer = self.env["res.partner"].create({"name": "WooCommerce customer"})
        self.env["woocommerce.res.partner"].create(
            {
                "backend_id": self.backend.id,
                "woocommerce_address_type": "billing",
                "woocommerce_address_hash": "30001",
                "name": "WooCommerce buyer",
                "type": "invoice",
                "parent_id": customer.id,
                "street": "Carrer de Mallorca 1",
            }
        )
        self.assertFalse(customer.street)

    def test_address_created_outside_the_import_gives_its_parent_its_address(self):
        customer = self.env["res.partner"].create({"name": "WooCommerce customer"})
        self.env["res.partner"].create(
            {
                "name": "WooCommerce buyer",
                "type": "invoice",
                "parent_id": customer.id,
                "street": "Carrer de Mallorca 1",
            }
        )
        self.assertEqual(customer.street, "Carrer de Mallorca 1")
