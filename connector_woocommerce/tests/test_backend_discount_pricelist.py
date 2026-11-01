# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from .common import WooCommerceCase


class TestBackendDiscountPricelist(WooCommerceCase):
    def test_backend_refuses_a_pricelist_of_another_company(self):
        company = self.env["res.company"].create({"name": "Other company"})
        pricelist = self.env["product.pricelist"].create(
            {"name": "Other company pricelist", "company_id": company.id}
        )
        with self.assertRaises(UserError):
            self.backend.discount_pricelist_id = pricelist

    def test_backend_takes_a_pricelist_of_its_company(self):
        pricelist = self.env["product.pricelist"].create(
            {
                "name": "Backend company pricelist",
                "company_id": self.backend.company_id.id,
            }
        )
        self.backend.discount_pricelist_id = pricelist
        self.assertEqual(self.backend.discount_pricelist_id, pricelist)

    def test_backend_takes_a_shared_pricelist(self):
        pricelist = self.env["product.pricelist"].create({"name": "Shared pricelist"})
        self.backend.discount_pricelist_id = pricelist
        self.assertEqual(self.backend.discount_pricelist_id, pricelist)
