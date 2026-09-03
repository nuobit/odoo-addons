# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError
from odoo.tests import Form, common


class TestSaleOrderInvoicingExclude(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test partner"})
        self.product = self.env["product.product"].create(
            {
                "name": "Test service",
                "type": "service",
                "invoice_policy": "order",
                "list_price": 100.0,
            }
        )
        self.order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 10.0,
                        },
                    )
                ],
            }
        )

    def _invoice_orders(self, orders):
        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(active_model="sale.order", active_ids=orders.ids)
            .create({"advance_payment_method": "delivered"})
        )
        wizard.create_invoices()

    def test_excluded_order_keeps_to_invoice_status(self):
        self.order.action_confirm()
        self.assertEqual(self.order.invoice_status, "to invoice")
        self.order.sale_invoicing_exclude_from_invoicing = True
        self.assertEqual(self.order.invoice_status, "to invoice")

    def test_excluded_order_is_skipped_by_invoicing(self):
        other_order = self.order.copy()
        orders = self.order | other_order
        orders.action_confirm()
        self.order.sale_invoicing_exclude_from_invoicing = True
        self._invoice_orders(orders)
        self.assertFalse(self.order.invoice_ids)
        self.assertEqual(self.order.invoice_status, "to invoice")
        self.assertEqual(len(other_order.invoice_ids), 1)
        self.assertEqual(other_order.invoice_status, "invoiced")

    def test_never_invoice_order_invoice_status(self):
        self.order.action_confirm()
        self.order.sale_invoicing_exclude_from_invoicing = True
        self.assertEqual(self.order.invoice_status, "to invoice")
        self.order.sale_invoicing_exclude_never_invoice = True
        self.assertEqual(self.order.invoice_status, "no")
        self.order.sale_invoicing_exclude_never_invoice = False
        self.assertEqual(self.order.invoice_status, "to invoice")

    def test_never_invoice_requires_exclusion(self):
        with self.assertRaises(ValidationError):
            self.order.sale_invoicing_exclude_never_invoice = True
        self.assertFalse(self.order.sale_invoicing_exclude_never_invoice)
        with self.assertRaises(ValidationError):
            self.order.copy({"sale_invoicing_exclude_never_invoice": True})
        self.order.write(
            {
                "sale_invoicing_exclude_from_invoicing": True,
                "sale_invoicing_exclude_never_invoice": True,
            }
        )
        with self.assertRaises(ValidationError):
            self.order.sale_invoicing_exclude_from_invoicing = False
        self.assertTrue(self.order.sale_invoicing_exclude_from_invoicing)
        self.assertTrue(self.order.sale_invoicing_exclude_never_invoice)

    def test_form_clears_never_invoice_with_exclusion(self):
        with Form(self.order) as order_form:
            order_form.sale_invoicing_exclude_from_invoicing = True
            order_form.sale_invoicing_exclude_never_invoice = True
        self.assertTrue(self.order.sale_invoicing_exclude_never_invoice)
        with Form(self.order) as order_form:
            order_form.sale_invoicing_exclude_from_invoicing = False
        self.assertFalse(self.order.sale_invoicing_exclude_from_invoicing)
        self.assertFalse(self.order.sale_invoicing_exclude_never_invoice)

    def test_excluded_invoiced_order_keeps_invoiced_status(self):
        self.order.action_confirm()
        self.order._create_invoices()
        self.assertEqual(self.order.invoice_status, "invoiced")
        self.order.sale_invoicing_exclude_from_invoicing = True
        self.assertEqual(self.order.invoice_status, "invoiced")
        self.order.sale_invoicing_exclude_never_invoice = True
        self.assertEqual(self.order.invoice_status, "invoiced")
