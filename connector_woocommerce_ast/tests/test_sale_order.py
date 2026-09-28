# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import WooCommerceAstCase


class TestSaleOrderDelivery(WooCommerceAstCase):
    def test_delivery_delivered_by_the_carrier_is_delivered(self):
        order = self._create_order({self.product_1: 1})
        order.action_confirm()
        self._validate(order.picking_ids)
        self.assertEqual(order.woocommerce_order_state, "done")
        self._carrier_reports(order.picking_ids, "customer_delivered")
        self.assertEqual(order.woocommerce_order_state, "delivered")

    def test_two_deliveries_delivered_in_one_update_are_delivered(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        picking = order.picking_ids
        self._validate(picking, {self.product_1: 1})
        backorder = order.picking_ids - picking
        self._validate(backorder)
        self.assertEqual(order.woocommerce_order_state, "done")
        self._carrier_reports(order.picking_ids, "customer_delivered")
        self.assertEqual(order.woocommerce_order_state, "delivered")

    def test_delivery_in_transit_is_done(self):
        order = self._create_order({self.product_1: 1})
        order.action_confirm()
        self._validate(order.picking_ids)
        self._carrier_reports(order.picking_ids, "in_transit")
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_delivery_without_a_carrier_is_done(self):
        order = self._create_order({self.product_1: 1})
        order.carrier_id = False
        order.action_confirm()
        self._validate(order.picking_ids)
        self.env["stock.picking"]._update_delivery_state()
        self.assertEqual(order.woocommerce_order_state, "done")
