# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from datetime import timedelta

from odoo import fields
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestRentalStatus(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_all = cls.env.ref("product.product_category_all")
        cls.rental_sale_type = cls.env.ref("rental_base.rental_sale_type")
        cls.uom_day = cls.env.ref("uom.product_uom_day")
        cls.warehouse0 = cls.env.ref("stock.warehouse0")
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@test.com",
            }
        )
        cls.product_hw = cls.env["product.product"].create(
            {
                "name": "Rental Hardware",
                "type": "product",
                "categ_id": cls.category_all.id,
            }
        )
        cls.service_rental = (
            cls.env["create.rental.product"]
            .with_context(active_model="product.product", active_id=cls.product_hw.id)
            .create(
                {
                    "hw_product_id": cls.product_hw.id,
                    "name": "Rental of Rental Hardware (Day)",
                    "categ_id": cls.product_hw.categ_id.id,
                    "copy_image": True,
                }
            )
            .create_rental_product()
        )
        cls.service_rental = cls.env["product.product"].browse(
            cls.service_rental["res_id"]
        )
        cls.service_rental.write(
            {
                "uom_id": cls.uom_day.id,
                "uom_po_id": cls.uom_day.id,
                "list_price": 100,
            }
        )
        cls.service_rental.rental = True

    def _create_rental_order(self, **kwargs):
        today = fields.Date.today()
        date_start = kwargs.get("date_start", today + timedelta(days=1))
        date_end = kwargs.get("date_end", today + timedelta(days=5))
        date_qty = (date_end - date_start).days + 1
        return self.env["sale.order"].create(
            {
                "type_id": self.rental_sale_type.id,
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "pricelist_id": self.env.ref("product.list0").id,
                "picking_policy": "direct",
                "warehouse_id": self.warehouse0.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Rental Service",
                            "product_id": self.service_rental.id,
                            "rental": True,
                            "rental_type": "new_rental",
                            "rental_qty": 1,
                            "product_uom_qty": date_qty,
                            "start_date": date_start,
                            "end_date": date_end,
                            "price_unit": 100,
                            "product_uom": self.uom_day.id,
                        },
                    )
                ],
            }
        )

    def _create_and_confirm_rental_order(self):
        order = self._create_rental_order()
        order.action_confirm()
        return order

    def test_confirmed_rental_status_pickup(self):
        """Confirmed rental with sale.rental records should have 'pickup' status."""
        order = self._create_and_confirm_rental_order()
        self.assertTrue(order.rental_ids)
        self.assertEqual(order.rental_status, "pickup")

    def test_confirmed_rental_status_pickup_product_without_rental_flag(self):
        """Confirmed rental with product missing rental=True on template
        should still be recognized as a rental order."""
        self.service_rental.rental = False
        order = self._create_and_confirm_rental_order()
        self.assertTrue(order.is_rental_order)
        self.assertTrue(order.rental_ids)
        self.assertEqual(order.rental_status, "pickup")

    def test_confirmed_rental_status_pickup_without_rental_records(self):
        """Confirmed rental order without sale.rental records should be 'pickup',
        not 'returned'. This happens when a product is not a proper rental
        service (missing rented_product_id) but the order is created from
        the rental menu."""
        order = self._create_and_confirm_rental_order()
        order.rental_ids.unlink()
        order._compute_rental_status()
        self.assertFalse(order.rental_ids)
        self.assertEqual(order.rental_status, "pickup")

    def test_rental_status_draft(self):
        """Draft rental order should have 'draft' status."""
        order = self._create_rental_order()
        self.assertEqual(order.rental_status, "draft")

    def test_rental_status_cancel(self):
        """Cancelled rental order should have 'cancel' status."""
        order = self._create_and_confirm_rental_order()
        order._action_cancel()
        self.assertEqual(order.rental_status, "cancel")

    def test_rental_status_return(self):
        """Rental with completed outgoing picking should have 'return' status."""
        order = self._create_and_confirm_rental_order()
        rental = order.rental_ids
        out_picking = rental.out_move_id.picking_id
        out_picking.action_assign()
        out_picking.move_ids.quantity_done = out_picking.move_ids.product_uom_qty
        out_picking.button_validate()
        self.assertEqual(order.rental_status, "return")

    def test_rental_status_returned(self):
        """Rental with both pickings completed should have 'returned' status."""
        order = self._create_and_confirm_rental_order()
        rental = order.rental_ids
        out_picking = rental.out_move_id.picking_id
        out_picking.action_assign()
        out_picking.move_ids.quantity_done = out_picking.move_ids.product_uom_qty
        out_picking.button_validate()
        in_picking = rental.in_move_id.picking_id
        in_picking.action_assign()
        in_picking.move_ids.quantity_done = in_picking.move_ids.product_uom_qty
        in_picking.button_validate()
        self.assertEqual(order.rental_status, "returned")
