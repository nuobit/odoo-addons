# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import WooCommerceCase


class TestImportMapperSaleOrder(WooCommerceCase):
    def _order_values(self, for_create=True):
        record = {
            "id": 5001,
            "billing": {},
            "shipping": {},
            "payment_method": "",
            "currency": self.env.company.currency_id.name,
            "customer_note": "",
            "status": "processing",
            "line_items": [],
        }
        with self.backend.work_on("woocommerce.sale.order") as work:
            mapper = work.component(usage="import.mapper")
            return mapper.map_record(record).values(for_create=for_create)

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

    def test_backend_without_discount_pricelist_maps_no_pricelist(self):
        self.backend.discount_pricelist_id = False
        self.assertNotIn("pricelist_id", self._order_values())
