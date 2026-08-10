# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import common


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

    def test_excluded_order_invoice_status(self):
        self.order.action_confirm()
        self.assertEqual(self.order.invoice_status, "to invoice")
        self.order.sale_invoicing_exclude_from_invoicing = True
        self.assertEqual(self.order.invoice_status, "no")
        self.order.sale_invoicing_exclude_from_invoicing = False
        self.assertEqual(self.order.invoice_status, "to invoice")

    def test_excluded_invoiced_order_keeps_invoiced_status(self):
        self.order.action_confirm()
        self.order._create_invoices()
        self.assertEqual(self.order.invoice_status, "invoiced")
        self.order.sale_invoicing_exclude_from_invoicing = True
        self.assertEqual(self.order.invoice_status, "invoiced")
