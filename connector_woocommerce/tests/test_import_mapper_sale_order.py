# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from .common import WooCommerceCase


class TestImportMapperSaleOrder(WooCommerceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.eur = cls.env.ref("base.EUR")
        cls.usd = cls.env.ref("base.USD")
        (cls.eur | cls.usd).write({"active": True})

    def _order_values(self, for_create=True, **record_values):
        record = {
            "id": 5001,
            "billing": {},
            "shipping": {},
            "payment_method": "",
            "currency": self.env.company.currency_id.name,
            "customer_note": "",
            "status": "processing",
            "line_items": [],
            **record_values,
        }
        with self.backend.work_on("woocommerce.sale.order") as work:
            mapper = work.component(usage="import.mapper")
            return mapper.map_record(record).values(for_create=for_create)

    def _bound_billing(self, pricelist):
        partner = self.env["res.partner"].create(
            {"name": "WooCommerce customer", "property_product_pricelist": pricelist.id}
        )
        self.env["woocommerce.res.partner"].create(
            {
                "backend_id": self.backend.id,
                "odoo_id": partner.id,
                "woocommerce_address_type": "billing",
                "woocommerce_address_hash": "5001",
            }
        )
        return {"type": "billing", "hash": "5001"}

    def test_order_gets_the_discount_pricelist(self):
        self.assertEqual(
            self._order_values()["pricelist_id"], self.discount_pricelist.id
        )

    def test_order_keeps_the_discount_pricelist_over_the_partner_one(self):
        partner = self.env["res.partner"].create(
            {
                "name": "WooCommerce customer",
                "property_product_pricelist": self.other_pricelist.id,
            }
        )
        values = self._order_values()
        order = self.env["sale.order"].create(
            {"partner_id": partner.id, "pricelist_id": values["pricelist_id"]}
        )
        self.assertEqual(order.pricelist_id, self.discount_pricelist)

    def test_order_update_keeps_its_pricelist(self):
        self.assertNotIn("pricelist_id", self._order_values(for_create=False))

    def test_order_without_discount_pricelist_gets_its_partner_pricelist(self):
        self.backend.discount_pricelist_id = False
        values = self._order_values(billing=self._bound_billing(self.other_pricelist))
        self.assertEqual(values["pricelist_id"], self.other_pricelist.id)

    def test_order_in_another_currency_than_its_pricelist_is_refused(self):
        self.discount_pricelist.currency_id = self.usd
        with self.assertRaisesRegex(ValidationError, "but its pricelist"):
            self._order_values(currency="EUR")

    def test_order_in_another_currency_than_its_partner_pricelist_is_refused(self):
        self.backend.discount_pricelist_id = False
        self.other_pricelist.currency_id = self.usd
        with self.assertRaisesRegex(ValidationError, "but its pricelist"):
            self._order_values(
                currency="EUR", billing=self._bound_billing(self.other_pricelist)
            )

    def test_order_without_any_pricelist_is_refused(self):
        self.backend.discount_pricelist_id = False
        with self.assertRaisesRegex(ValidationError, "gets no pricelist"):
            self._order_values()
