# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestSaleOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "WooCommerce Test Customer",
            }
        )
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.picking_type.default_location_src_id

    def _create_woocommerce_order(self, picking_state):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "is_woocommerce": True,
            }
        )
        self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.picking_type.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "sale_id": order.id,
                "state": picking_state,
            }
        )
        return order

    def test_compute_woocommerce_order_state_uses_current_order_pickings(self):
        processing_order = self._create_woocommerce_order("assigned")
        done_order = self._create_woocommerce_order("done")
        orders = processing_order | done_order

        orders._compute_woocommerce_order_state()

        self.assertEqual(processing_order.woocommerce_order_state, "processing")
        self.assertEqual(done_order.woocommerce_order_state, "done")
        self.assertEqual(processing_order.done_picking_count, 0)
        self.assertEqual(done_order.done_picking_count, 1)
