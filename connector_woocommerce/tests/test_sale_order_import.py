# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from .common import WooCommerceSaleOrderImportCase


class TestSaleOrderImport(WooCommerceSaleOrderImportCase):
    def _all_contacts(self):
        return self.env["res.partner"].with_context(active_test=False).search([])

    def test_new_buyer_gets_a_customer_with_its_two_addresses(self):
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com", phone="600000001"
            ),
            shipping=self._address_block("WooCommerce", "buyer", phone="600000002"),
        )
        self._import_order(order)
        sale = self._imported_order(order)
        customer = sale.partner_id
        self.assertEqual(customer.name, "WooCommerce buyer")
        self.assertFalse(customer.parent_id)
        self.assertEqual(customer.company_type, "company")
        # Odoo gives a contact with no address the one of its first child
        self.assertEqual(customer.street, "Carrer de Mallorca 1")
        self.assertFalse(customer.phone)
        self.assertFalse(customer.mobile)
        self.assertFalse(customer.email)
        invoice_address = sale.partner_invoice_id
        self.assertEqual(invoice_address.parent_id, customer)
        self.assertEqual(invoice_address.type, "invoice")
        self.assertEqual(invoice_address.name, "WooCommerce buyer")
        self.assertEqual(invoice_address.email, "buyer@example.com")
        self.assertEqual(invoice_address.mobile, "600000001")
        self.assertFalse(invoice_address.phone)
        delivery_address = sale.partner_shipping_id
        self.assertEqual(delivery_address.parent_id, customer)
        self.assertEqual(delivery_address.type, "delivery")
        self.assertEqual(delivery_address.mobile, "600000002")
        self.assertFalse(delivery_address.phone)
        self.assertEqual(customer.child_ids, invoice_address | delivery_address)
        self.assertEqual(sale.payment_mode_id, self.card)
        self.assertEqual(sale.pricelist_id, self.discount_pricelist)
        self.assertEqual(sale.client_order_ref, "WC-30001")
        self.assertEqual(sale.state, "sale")

    def test_same_blocks_again_reuse_their_contacts(self):
        billing = self._address_block("WooCommerce", "buyer", email="buyer@example.com")
        shipping = self._address_block("WooCommerce", "buyer")
        first_order = self._shop_order(30001, billing, shipping)
        second_order = self._shop_order(30002, billing, shipping)
        self._import_order(first_order)
        contacts = self._all_contacts()
        self._import_order(second_order)
        self.assertEqual(self._all_contacts(), contacts)
        first_sale = self._imported_order(first_order)
        second_sale = self._imported_order(second_order)
        self.assertEqual(second_sale.partner_id, first_sale.partner_id)
        self.assertEqual(second_sale.partner_invoice_id, first_sale.partner_invoice_id)
        self.assertEqual(
            second_sale.partner_shipping_id, first_sale.partner_shipping_id
        )

    def test_billing_company_names_the_customer(self):
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce",
                "buyer",
                company="WooCommerce company",
                email="buyer@example.com",
            ),
            shipping=self._address_block(
                "WooCommerce", "buyer", company="WooCommerce company"
            ),
        )
        self._import_order(order)
        sale = self._imported_order(order)
        self.assertEqual(sale.partner_id.name, "WooCommerce company")
        self.assertEqual(sale.partner_invoice_id.name, "WooCommerce buyer")
        self.assertEqual(sale.partner_shipping_id.parent_id, sale.partner_id)

    def test_contact_with_the_buyer_name_and_addresses_is_the_customer(self):
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
        self.assertEqual(sale.partner_invoice_id.parent_id, customer)
        self.assertEqual(sale.partner_shipping_id.parent_id, customer)

    def test_contact_with_the_buyer_name_and_no_addresses_is_not_the_customer(self):
        namesake = self.env["res.partner"].create({"name": "WooCommerce buyer"})
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
        )
        self._import_order(order)
        sale = self._imported_order(order)
        self.assertNotEqual(sale.partner_id, namesake)
        self.assertEqual(sale.partner_id.name, "WooCommerce buyer")
        self.assertFalse(namesake.child_ids)

    def test_two_contacts_with_the_buyer_name_stop_the_import(self):
        for _contact in range(2):
            self.env["res.partner"].create(
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
        with self.assertRaisesRegex(
            ValidationError,
            "There are more than one parent partner with the same name "
            "WooCommerce buyer",
        ):
            self._import_order(order)

    def test_delivery_to_another_name_gets_a_customer_of_its_own(self):
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "recipient"),
        )
        self._import_order(order)
        sale = self._imported_order(order)
        delivery_customer = sale.partner_shipping_id.parent_id
        self.assertEqual(delivery_customer.name, "WooCommerce recipient")
        self.assertNotEqual(delivery_customer, sale.partner_id)

    def test_imported_order_is_not_imported_again(self):
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
        )
        self._import_order(order)
        sale = self._imported_order(order)
        contacts = self._all_contacts()
        result = self._import_order(order)
        self.assertEqual(
            result,
            "The Order %s is already imported -> Update not allowed"
            % sale.display_name,
        )
        self.assertEqual(self._all_contacts(), contacts)
        self.assertEqual(self._imported_order(order), sale)

    def test_unmapped_payment_method_stops_the_import(self):
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
        )
        order["payment_method"] = "paypal"
        with self.assertRaisesRegex(
            ValidationError, "Payment method 'paypal' is not defined on backend"
        ):
            self._import_order(order)

    def test_order_without_payment_method_gets_no_payment_mode(self):
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
        )
        order["payment_method"] = ""
        self._import_order(order)
        self.assertFalse(self._imported_order(order).payment_mode_id)
