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

    def test_done_delivery_with_service_lines_is_done(self):
        service_on_delivery = self.env["product.product"].create(
            {
                "name": "Service invoiced on delivery",
                "type": "service",
                "invoice_policy": "delivery",
            }
        )
        service_on_order = self.env["product.product"].create(
            {
                "name": "Service invoiced on order",
                "type": "service",
                "invoice_policy": "order",
            }
        )
        order = self._create_order(
            {self.product_1: 1, service_on_delivery: 1, service_on_order: 1}
        )
        order.action_confirm()
        self._validate(order.picking_ids)
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_delivered_delivery_with_service_lines_is_delivered(self):
        service_on_delivery = self.env["product.product"].create(
            {
                "name": "Service invoiced on delivery",
                "type": "service",
                "invoice_policy": "delivery",
            }
        )
        service_on_order = self.env["product.product"].create(
            {
                "name": "Service invoiced on order",
                "type": "service",
                "invoice_policy": "order",
            }
        )
        order = self._create_order(
            {self.product_1: 1, service_on_delivery: 1, service_on_order: 1}
        )
        order.action_confirm()
        self._validate(order.picking_ids)
        self._carrier_reports(order.picking_ids, "customer_delivered")
        self.assertEqual(order.woocommerce_order_state, "delivered")

    def test_return_validated_updating_quantities_keeps_the_order_done(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery)
        return_picking = self._create_return(delivery)
        self._validate(return_picking)
        self.assertEqual(order.order_line.mapped("qty_delivered"), [0.0, 0.0])
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_backorder_validated_after_a_return_is_done(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery, {self.product_1: 1})
        backorder = order.picking_ids - delivery
        return_picking = self._create_return(delivery)
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        self._validate(return_picking)
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        self._validate(backorder)
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_replacement_validated_after_a_return_is_done(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery)
        return_picking = self._create_return(delivery)
        self._validate(return_picking)
        self.assertEqual(order.woocommerce_order_state, "done")
        replacement = self._create_return(return_picking)
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        self._validate(replacement)
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_delivered_replacement_of_a_delivered_delivery_is_delivered(self):
        order = self._create_order({self.product_1: 1})
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery)
        self._carrier_reports(delivery, "customer_delivered")
        return_picking = self._create_return(delivery)
        self._validate(return_picking)
        self.assertEqual(order.woocommerce_order_state, "delivered")
        replacement = self._create_return(return_picking)
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        replacement.carrier_id = self.carrier
        self._validate(replacement)
        self.assertEqual(order.woocommerce_order_state, "done")
        self._carrier_reports(replacement, "customer_delivered")
        self.assertEqual(order.woocommerce_order_state, "delivered")

    def test_return_of_the_replacement_keeps_the_order_done(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery)
        return_picking = self._create_return(delivery)
        self._validate(return_picking)
        replacement = self._create_return(return_picking)
        self._validate(replacement)
        second_return = self._create_return(replacement)
        self._validate(second_return)
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_return_of_a_delivered_delivery_keeps_the_order_delivered(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery)
        self._carrier_reports(delivery, "customer_delivered")
        return_picking = self._create_return(delivery)
        self.assertEqual(order.woocommerce_order_state, "delivered")
        self._validate(return_picking)
        self.assertEqual(order.woocommerce_order_state, "delivered")

    def test_part_of_a_line_shipped_in_the_backorder_is_done(self):
        order = self._create_order(
            {self.product_1: 2, self.product_2: 3, self.product_3: 1}
        )
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(
            delivery, {self.product_1: 2, self.product_2: 2, self.product_3: 1}
        )
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        self._validate(order.picking_ids - delivery)
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_part_of_a_line_not_shipped_is_done(self):
        order = self._create_order(
            {self.product_1: 2, self.product_2: 3, self.product_3: 1}
        )
        order.action_confirm()
        self._validate(
            order.picking_ids,
            {self.product_1: 2, self.product_2: 2, self.product_3: 1},
            backorder=False,
        )
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_line_cancelled_in_the_backorder_is_done(self):
        order = self._create_order(
            {self.product_1: 2, self.product_2: 3, self.product_3: 1}
        )
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery, {self.product_1: 2})
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        self._validate(
            order.picking_ids - delivery, {self.product_2: 3}, backorder=False
        )
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_backorder_split_again_is_done(self):
        order = self._create_order(
            {self.product_1: 2, self.product_2: 3, self.product_3: 1}
        )
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery, {self.product_1: 2})
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        backorder_1 = order.picking_ids - delivery
        self._validate(backorder_1, {self.product_2: 1})
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        self._validate(order.picking_ids - delivery - backorder_1)
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_last_backorder_cancelled_is_done(self):
        order = self._create_order(
            {self.product_1: 2, self.product_2: 3, self.product_3: 1}
        )
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery, {self.product_1: 2})
        backorder_1 = order.picking_ids - delivery
        self._validate(backorder_1, {self.product_2: 1})
        backorder_2 = order.picking_ids - delivery - backorder_1
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        backorder_2.action_cancel()
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_last_backorder_partly_cancelled_is_done(self):
        order = self._create_order(
            {self.product_1: 2, self.product_2: 3, self.product_3: 1}
        )
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery, {self.product_1: 2})
        backorder_1 = order.picking_ids - delivery
        self._validate(backorder_1, {self.product_2: 1})
        backorder_2 = order.picking_ids - delivery - backorder_1
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        self._validate(backorder_2, {self.product_3: 1}, backorder=False)
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_only_delivery_cancelled_is_cancel(self):
        order = self._create_order(
            {self.product_1: 2, self.product_2: 3, self.product_3: 1}
        )
        order.action_confirm()
        order.picking_ids.action_cancel()
        self.assertEqual(order.woocommerce_order_state, "cancel")

    def test_last_backorder_validated_after_a_return_is_done(self):
        order = self._create_order(
            {self.product_1: 2, self.product_2: 3, self.product_3: 1}
        )
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery, {self.product_1: 2})
        backorder_1 = order.picking_ids - delivery
        self._validate(backorder_1, {self.product_2: 1})
        backorder_2 = order.picking_ids - delivery - backorder_1
        return_picking = self._create_return(delivery, {self.product_1: 1})
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        self._validate(return_picking)
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        self._validate(backorder_2)
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_return_after_a_delivery_without_backorder_keeps_the_order_delivered(self):
        order = self._create_order(
            {self.product_1: 2, self.product_2: 3, self.product_3: 1}
        )
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(
            delivery,
            {self.product_1: 2, self.product_2: 2, self.product_3: 1},
            backorder=False,
        )
        self._carrier_reports(delivery, "customer_delivered")
        self.assertEqual(order.woocommerce_order_state, "delivered")
        return_picking = self._create_return(delivery, {self.product_1: 1})
        self._validate(return_picking)
        self.assertEqual(order.woocommerce_order_state, "delivered")

    def test_ordered_quantity_lowered_before_shipping_is_done(self):
        order = self._create_order(
            {self.product_1: 2, self.product_2: 3, self.product_3: 1}
        )
        order.action_confirm()
        line_2 = order.order_line.filtered(
            lambda line: line.product_id == self.product_2
        )
        line_2.product_uom_qty = 2
        self._validate(
            order.picking_ids,
            {self.product_1: 2, self.product_2: 2, self.product_3: 1},
            backorder=False,
        )
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_ordered_quantity_raised_after_shipping_is_done(self):
        order = self._create_order(
            {self.product_1: 2, self.product_2: 3, self.product_3: 1}
        )
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery)
        self.assertEqual(order.woocommerce_order_state, "done")
        line_1 = order.order_line.filtered(
            lambda line: line.product_id == self.product_1
        )
        line_1.product_uom_qty = 3
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        self._validate(order.picking_ids - delivery)
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_line_added_after_shipping_is_done(self):
        order = self._create_order(
            {self.product_1: 2, self.product_2: 3, self.product_3: 1}
        )
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery)
        self.assertEqual(order.woocommerce_order_state, "done")
        product_4 = self._create_storable_product("WooCommerce product 4")
        self.env["sale.order.line"].create(
            {"order_id": order.id, "product_id": product_4.id, "product_uom_qty": 1}
        )
        self.assertEqual(order.woocommerce_order_state, "partial_shipped")
        self._validate(order.picking_ids - delivery)
        self.assertEqual(order.woocommerce_order_state, "done")

    def test_return_of_part_of_a_line_keeps_the_order_done(self):
        order = self._create_order(
            {self.product_1: 2, self.product_2: 3, self.product_3: 1}
        )
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery)
        return_picking = self._create_return(delivery, {self.product_2: 1})
        self._validate(return_picking)
        self.assertEqual(order.woocommerce_order_state, "done")
