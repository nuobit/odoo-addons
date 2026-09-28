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

    def test_done_delivery_with_a_pending_backorder_is_partial_shipped(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        self._validate(order.picking_ids, {self.product_1: 1})
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")

    def test_done_delivery_and_done_backorder_are_done(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        picking = order.picking_ids
        self._validate(picking, {self.product_1: 1})
        backorder = order.picking_ids - picking
        self._validate(backorder)
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_delivered_delivery_with_a_pending_backorder_is_partial_shipped(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        picking = order.picking_ids
        self._validate(picking, {self.product_1: 1})
        self._carrier_reports(picking, "customer_delivered")
        self.assertEqual(picking.woocommerce_stock_picking_state, "delivered")
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")

    def test_delivered_delivery_and_delivered_backorder_are_delivered(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        picking = order.picking_ids
        self._validate(picking, {self.product_1: 1})
        self._carrier_reports(picking, "customer_delivered")
        backorder = order.picking_ids - picking
        self._validate(backorder)
        self.assertEqual(order.woocommerce_order_state, "done")
        self._carrier_reports(backorder, "customer_delivered")
        self.assertEqual(order.woocommerce_order_state, "delivered")

    def test_done_delivery_with_a_cancelled_backorder_is_done(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        picking = order.picking_ids
        self._validate(picking, {self.product_1: 1})
        backorder = order.picking_ids - picking
        backorder.action_cancel()
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_delivered_delivery_with_a_cancelled_backorder_is_delivered(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        picking = order.picking_ids
        self._validate(picking, {self.product_1: 1})
        backorder = order.picking_ids - picking
        backorder.action_cancel()
        self.assertEqual(order.woocommerce_order_state, "done")
        self._carrier_reports(picking, "customer_delivered")
        self.assertEqual(order.woocommerce_order_state, "delivered")

    def test_split_backorder_delivered_in_steps_is_partial_shipped(self):
        order = self._create_order(
            {self.product_1: 2, self.product_2: 3, self.product_3: 1}
        )
        order.action_confirm()
        picking = order.picking_ids
        self._validate(picking, {self.product_1: 2})
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        self._carrier_reports(picking, "customer_delivered")
        self.assertEqual(picking.woocommerce_stock_picking_state, "delivered")
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        backorder_1 = order.picking_ids - picking
        self._validate(backorder_1, {self.product_2: 1})
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        self._carrier_reports(backorder_1, "customer_delivered")
        self.assertEqual(backorder_1.woocommerce_stock_picking_state, "delivered")
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")

    def test_split_backorder_delivered_with_the_last_cancelled_is_delivered(self):
        order = self._create_order(
            {self.product_1: 2, self.product_2: 3, self.product_3: 1}
        )
        order.action_confirm()
        picking = order.picking_ids
        self._validate(picking, {self.product_1: 2})
        self._carrier_reports(picking, "customer_delivered")
        backorder_1 = order.picking_ids - picking
        self._validate(backorder_1, {self.product_2: 1})
        self._carrier_reports(backorder_1, "customer_delivered")
        backorder_2 = order.picking_ids - picking - backorder_1
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        backorder_2.action_cancel()
        self.assertEqual(order.woocommerce_order_state, "delivered")

    def test_done_pick_of_a_two_step_delivery_is_processing(self):
        order = self._create_order({self.product_1: 1})
        order.warehouse_id.delivery_steps = "pick_ship"
        order.action_confirm()
        pick = order.picking_ids.filtered(
            lambda p: p.picking_type_id == order.warehouse_id.pick_type_id
        )
        self._validate(pick)
        self.assertEqual(pick.state, "done")
        self.assertEqual(order.woocommerce_order_state, "processing")

    def test_done_ship_of_a_two_step_delivery_is_done(self):
        order = self._create_order({self.product_1: 1})
        order.warehouse_id.delivery_steps = "pick_ship"
        order.action_confirm()
        pick = order.picking_ids.filtered(
            lambda p: p.picking_type_id == order.warehouse_id.pick_type_id
        )
        self._validate(pick)
        self._validate(order.picking_ids - pick)
        self.assertEqual(order.woocommerce_order_state, "done")
