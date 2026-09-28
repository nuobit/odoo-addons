# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase

from .common import WooCommerceOrderCase


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

    def test_create_line_as_salesperson_without_settings_group(self):
        """Saving a sale order line must not require ORM access to
        ``decimal.precision``.

        Regression: ``create``/``write`` read the Discount precision via
        ``self.env.ref("product.decimal_discount").digits`` (an ORM read of a
        ``decimal.precision`` record), which raised AccessError for users
        without the Settings group (``base.group_system``).
        """
        salesperson = self.env["res.users"].create(
            {
                "name": "Salesperson Without Settings",
                "login": "wc_salesperson_no_settings",
                "groups_id": [
                    (6, 0, [self.env.ref("sales_team.group_sale_salesman").id])
                ],
            }
        )
        product = self.env["product.product"].create({"name": "WC Test Product"})
        line_vals = {
            "product_id": product.id,
            "product_uom_qty": 1.0,
            "discount": 10.0,
        }
        order = (
            self.env["sale.order"]
            .with_user(salesperson)
            .create(
                {
                    "partner_id": self.partner.id,
                    "order_line": [(0, 0, line_vals)],
                }
            )
        )
        self.assertEqual(len(order.order_line), 1)


class TestSaleOrderDelivery(WooCommerceOrderCase):
    def test_one_product_shipped_in_one_delivery_is_done(self):
        order = self._create_order({self.product_1: 1})
        order.action_confirm()
        self.assertEqual(order.woocommerce_order_state, "processing")
        self._validate(order.picking_ids)
        self.assertEqual(order.woocommerce_order_state, "done")
        self.assertEqual(order.done_picking_count, 1)

    def test_two_products_shipped_in_one_delivery_are_done(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        self.assertEqual(order.woocommerce_order_state, "processing")
        self._validate(order.picking_ids)
        self.assertEqual(order.woocommerce_order_state, "done")
        self.assertEqual(order.done_picking_count, 1)

    def test_product_not_shipped_without_backorder_is_done(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        self._validate(order.picking_ids, {self.product_1: 1}, backorder=False)
        self.assertEqual(order.woocommerce_order_state, "done")
        self.assertEqual(order.done_picking_count, 1)

    def test_order_cancelled_before_shipping_is_cancel(self):
        order = self._create_order({self.product_1: 1})
        order.action_confirm()
        self.assertEqual(order.woocommerce_order_state, "processing")
        order.action_cancel()
        self.assertEqual(order.woocommerce_order_state, "cancel")
        self.assertEqual(order.done_picking_count, 0)

    def test_return_left_open_keeps_the_order_done(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery)
        self._create_return(delivery)
        self.assertEqual(order.woocommerce_order_state, "done")
        self.assertEqual(order.done_picking_count, 1)

    def test_partial_return_left_open_keeps_the_order_done(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery)
        self._create_return(delivery, {self.product_1: 1})
        self.assertEqual(order.woocommerce_order_state, "done")
        self.assertEqual(order.done_picking_count, 1)

    def test_return_validated_without_updating_quantities_keeps_the_order_done(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery)
        return_picking = self._create_return(delivery, to_refund=False)
        self._validate(return_picking)
        self.assertEqual(order.order_line.mapped("qty_delivered"), [1.0, 1.0])
        self.assertEqual(order.woocommerce_order_state, "done")
        self.assertEqual(order.done_picking_count, 1)

    def test_return_cancelled_keeps_the_order_done(self):
        order = self._create_order({self.product_1: 1, self.product_2: 1})
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery)
        return_picking = self._create_return(delivery)
        return_picking.action_cancel()
        self.assertEqual(order.woocommerce_order_state, "done")
        self.assertEqual(order.done_picking_count, 1)

    def test_done_delivery_queues_the_export_of_the_bound_order(self):
        order = self._create_order({self.product_1: 1})
        self._bind_order(order, 3001)
        order.action_confirm()
        self.assertEqual(order.woocommerce_order_state, "processing")
        job = self._new_job(
            "woocommerce.sale.order",
            "export_batch",
            lambda: self._validate(order.picking_ids),
        )
        self.assertEqual(order.woocommerce_order_state, "done")
        self.assertEqual(self.env["sale.order"].search(job.kwargs["domain"]), order)

    def test_return_queues_no_export(self):
        order = self._create_order({self.product_1: 1})
        self._bind_order(order, 3001)
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery)
        jobs = self._new_jobs(
            "woocommerce.sale.order",
            "export_batch",
            lambda: self._create_return(delivery, to_refund=False),
        )
        self.assertFalse(jobs)
        return_picking = order.picking_ids - delivery
        jobs = self._new_jobs(
            "woocommerce.sale.order",
            "export_batch",
            lambda: self._validate(return_picking),
        )
        self.assertFalse(jobs)

    def test_second_done_shipment_queues_an_export(self):
        order = self._create_order(
            {self.product_1: 1, self.product_2: 1, self.product_3: 1}
        )
        self._bind_order(order, 3001)
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery, {self.product_1: 1})
        backorder_1 = order.picking_ids - delivery
        self._new_job(
            "woocommerce.sale.order",
            "export_batch",
            lambda: self._validate(backorder_1, {self.product_2: 1}),
        )
        self.assertEqual(order.done_picking_count, 2)

    def test_validated_return_with_a_pending_backorder_queues_no_export(self):
        order = self._create_order(
            {self.product_1: 1, self.product_2: 1, self.product_3: 1}
        )
        self._bind_order(order, 3001)
        order.action_confirm()
        delivery = order.picking_ids
        self._validate(delivery, {self.product_1: 1})
        backorder_1 = order.picking_ids - delivery
        self._validate(backorder_1, {self.product_2: 1})
        return_picking = self._create_return(delivery)
        jobs = self._new_jobs(
            "woocommerce.sale.order",
            "export_batch",
            lambda: self._validate(return_picking),
        )
        self.assertFalse(jobs)
        self.assertEqual(order.done_picking_count, 2)
