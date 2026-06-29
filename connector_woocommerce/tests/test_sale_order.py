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

    def _create_order(self, is_woocommerce=True, cancel_picking=False):
        vals = {
            "partner_id": self.partner.id,
            "is_woocommerce": is_woocommerce,
        }
        order = self.env["sale.order"].create(vals)
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.picking_type.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "sale_id": order.id,
            }
        )
        if cancel_picking:
            picking.action_cancel()
        return order

    def test_compute_woocommerce_order_state_uses_current_order_pickings(self):
        processing_order = self._create_order()
        cancel_order = self._create_order(cancel_picking=True)
        orders = processing_order | cancel_order

        orders._compute_woocommerce_order_state()

        self.assertEqual(processing_order.woocommerce_order_state, "processing")
        self.assertEqual(cancel_order.woocommerce_order_state, "cancel")
        self.assertEqual(processing_order.done_picking_count, 0)
        self.assertEqual(cancel_order.done_picking_count, 0)

    def test_compute_woocommerce_fields_ignore_non_woocommerce_orders(self):
        woocommerce_order = self._create_order()
        sale_order = self._create_order(is_woocommerce=False)
        orders = woocommerce_order | sale_order

        orders._compute_woocommerce_status_write_date()
        orders._compute_woocommerce_order_state()

        self.assertTrue(woocommerce_order.woocommerce_status_write_date)
        self.assertEqual(woocommerce_order.woocommerce_order_state, "processing")
        self.assertFalse(sale_order.woocommerce_status_write_date)
        self.assertFalse(sale_order.woocommerce_order_state)
        self.assertEqual(sale_order.done_picking_count, 0)
