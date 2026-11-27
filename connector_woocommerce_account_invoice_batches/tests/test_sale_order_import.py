# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.connector_woocommerce.tests.common import (
    WooCommerceSaleOrderImportCase,
)


class TestSaleOrderImportInvoiceBatches(WooCommerceSaleOrderImportCase):
    def test_new_customer_and_its_invoice_address_get_the_backend_method(self):
        self.backend.invoice_batch_sending_method = "email"
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
        )
        self._import_order(order)
        sale = self._imported_order(order)
        customer = sale.partner_id
        self.assertEqual(customer.invoice_batch_sending_method, "email")
        self.assertEqual(customer.invoice_batch_email_partner_id, customer)
        invoice_address = sale.partner_invoice_id
        self.assertEqual(invoice_address.invoice_batch_sending_method, "email")
        self.assertEqual(
            invoice_address.invoice_batch_email_partner_id, invoice_address
        )
        delivery_address = sale.partner_shipping_id
        self.assertEqual(delivery_address.invoice_batch_sending_method, "pdf")
        self.assertFalse(delivery_address.invoice_batch_email_partner_id)

    def test_found_customer_keeps_its_method_and_its_new_invoice_address_gets_it(
        self,
    ):
        self.backend.invoice_batch_sending_method = "email"
        customer = self.env["res.partner"].create(
            {
                "name": "WooCommerce buyer",
                "child_ids": [(0, 0, {"name": "WooCommerce contact person"})],
            }
        )
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
        )
        self._import_order(order)
        sale = self._imported_order(order)
        self.assertEqual(sale.partner_id, customer)
        self.assertEqual(customer.invoice_batch_sending_method, "pdf")
        self.assertFalse(customer.invoice_batch_email_partner_id)
        invoice_address = sale.partner_invoice_id
        self.assertEqual(invoice_address.invoice_batch_sending_method, "email")
        self.assertEqual(
            invoice_address.invoice_batch_email_partner_id, invoice_address
        )

    def test_backend_without_method_leaves_the_contacts_their_own(self):
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
        )
        self._import_order(order)
        sale = self._imported_order(order)
        self.assertEqual(sale.partner_id.invoice_batch_sending_method, "pdf")
        self.assertFalse(sale.partner_id.invoice_batch_email_partner_id)
        self.assertEqual(sale.partner_invoice_id.invoice_batch_sending_method, "pdf")
        self.assertFalse(sale.partner_invoice_id.invoice_batch_email_partner_id)
