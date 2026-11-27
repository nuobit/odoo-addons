# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.exceptions import ValidationError

from odoo.addons.connector_woocommerce.tests.common import (
    WooCommerceSaleOrderImportCase,
)

# Valid Spanish fixtures: a person's NIF, a foreigner's NIE and a company's CIF
FIXTURE_NIF = "12345678Z"
FIXTURE_NIE = "X1234567L"
FIXTURE_CIF = "B12345674"


class TestSaleOrderImportNif(WooCommerceSaleOrderImportCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The backend's company is a Spanish one
        cls.env.company.country_id = cls.env.ref("base.es")

    def _all_contacts(self):
        return self.env["res.partner"].with_context(active_test=False).search([])

    def _nif(self, nif):
        """The checkout's NIF, as the shop keeps it in the order's meta data."""
        return [{"id": 1, "key": "_billing_nif", "value": nif}]

    def _customer_with_vat(self, vat, name="WooCommerce clinic"):
        return self.env["res.partner"].create(
            {
                "name": name,
                "company_type": "company",
                "country_id": self.env.ref("base.es").id,
                "vat": vat,
            }
        )

    def _contact_lines(self, *contacts):
        """The error's lines for the contacts, as Odoo names each one: a module
        may add to the name, as partner_name_vat adds the Tax ID."""
        return "".join(
            "\n- %s %s" % (contact.id, contact.display_name) for contact in contacts
        )

    def test_new_buyer_gets_its_nif_with_the_country_code(self):
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
            meta_data=self._nif(FIXTURE_NIF),
        )
        self._import_order(order)
        sale = self._imported_order(order)
        self.assertEqual(sale.partner_id.vat, "ES12345678Z")
        self.assertEqual(sale.partner_invoice_id.vat, "ES12345678Z")
        self.assertEqual(sale.partner_shipping_id.vat, "ES12345678Z")

    def test_nif_is_worked_out_once_per_import(self):
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
            meta_data=self._nif(FIXTURE_NIF),
        )
        partner_class = type(self.env["res.partner"])
        with patch.object(
            partner_class,
            "_woocommerce_vat_number",
            autospec=True,
            side_effect=partner_class._woocommerce_vat_number,
        ) as vat_number:
            self._import_order(order)
        self.assertEqual(vat_number.call_count, 1)

    def test_nie_with_a_french_address_gets_the_company_country_code(self):
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce",
                "buyer",
                email="buyer@example.com",
                address_1="Rue de Rivoli 1",
                city="Paris",
                state="",
                postcode="75001",
                country="FR",
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
            meta_data=self._nif(FIXTURE_NIE),
        )
        self._import_order(order)
        self.assertEqual(self._imported_order(order).partner_id.vat, "ESX1234567L")

    def test_nif_billed_outside_europe_is_kept_as_typed(self):
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce",
                "buyer",
                email="buyer@example.com",
                address_1="5th Avenue 1",
                city="New York",
                state="",
                postcode="10001",
                country="US",
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
            meta_data=self._nif(FIXTURE_NIF),
        )
        self._import_order(order)
        self.assertEqual(self._imported_order(order).partner_id.vat, "12345678Z")

    def test_nif_billed_outside_europe_finds_the_customer_stored_with_its_code(
        self,
    ):
        customer = self._customer_with_vat("ES12345678Z")
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce",
                "buyer",
                email="buyer@example.com",
                address_1="5th Avenue 1",
                city="New York",
                state="",
                postcode="10001",
                country="US",
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
            meta_data=self._nif(FIXTURE_NIF),
        )
        self._import_order(order)
        self.assertEqual(self._imported_order(order).partner_id, customer)

    def test_invalid_nif_stops_the_import_with_odoo_s_error(self):
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
            meta_data=self._nif("12345678A"),
        )
        with self.assertRaisesRegex(
            ValidationError,
            r"The VAT number \[ES12345678A\] for partner \[WooCommerce buyer\] does "
            "not seem to be valid",
        ):
            # The job's transaction, which the error rolls back
            with self.env.cr.savepoint():
                self._import_order(order)
        self.assertFalse(
            self.env["res.partner"].search([("name", "=", "WooCommerce buyer")])
        )

    def test_new_buyer_with_a_nif_gets_the_position_that_requires_one(self):
        self.env["account.fiscal.position"].search([("auto_apply", "=", True)]).write(
            {"auto_apply": False}
        )
        national = self.env["account.fiscal.position"].create(
            {
                "name": "WooCommerce national",
                "auto_apply": True,
                "vat_required": True,
                "country_id": self.env.ref("base.es").id,
            }
        )
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
            meta_data=self._nif(FIXTURE_NIF),
        )
        self._import_order(order)
        sale = self._imported_order(order)
        self.assertEqual(sale.partner_id.property_account_position_id, national)
        self.assertEqual(sale.fiscal_position_id, national)

    def test_customer_found_by_its_nif_keeps_its_values(self):
        customer = self._customer_with_vat("ESB12345674")
        customer.write(
            {
                "user_id": self.salesperson.id,
                "property_payment_term_id": self.immediate_payment.id,
                "property_product_pricelist": self.other_pricelist.id,
            }
        )
        self.backend.salesperson_id = self.env.user
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "recipient"),
            meta_data=self._nif(FIXTURE_CIF),
        )
        contacts = self._all_contacts()
        self._import_order(order)
        sale = self._imported_order(order)
        self.assertEqual(sale.partner_id, customer)
        self.assertEqual(
            self._all_contacts() - contacts,
            sale.partner_invoice_id | sale.partner_shipping_id,
        )
        self.assertEqual(sale.partner_invoice_id.parent_id, customer)
        self.assertEqual(sale.partner_shipping_id.parent_id, customer)
        self.assertEqual(customer.name, "WooCommerce clinic")
        self.assertEqual(customer.vat, "ESB12345674")
        self.assertEqual(customer.user_id, self.salesperson)
        self.assertEqual(customer.property_payment_term_id, self.immediate_payment)
        self.assertEqual(customer.property_product_pricelist, self.other_pricelist)

    def test_nif_finds_a_vat_number_stored_without_code(self):
        customer = self._customer_with_vat("B12345674")
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
            meta_data=self._nif(FIXTURE_CIF),
        )
        self._import_order(order)
        self.assertEqual(self._imported_order(order).partner_id, customer)

    def test_nif_finds_a_vat_number_stored_with_dashes(self):
        customer = self._customer_with_vat("b-12345674")
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
            meta_data=self._nif(FIXTURE_CIF),
        )
        self._import_order(order)
        self.assertEqual(self._imported_order(order).partner_id, customer)

    def test_nif_finds_a_vat_number_stored_with_spaces(self):
        customer = self._customer_with_vat("B 12345674")
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
            meta_data=self._nif(FIXTURE_CIF),
        )
        self._import_order(order)
        self.assertEqual(self._imported_order(order).partner_id, customer)

    def test_nif_typed_with_its_code_finds_a_vat_number_stored_without(self):
        customer = self._customer_with_vat("B12345674")
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
            meta_data=self._nif("es-b12345674"),
        )
        self._import_order(order)
        self.assertEqual(self._imported_order(order).partner_id, customer)

    def test_two_contacts_with_the_nif_stop_the_import_naming_both(self):
        first = self._customer_with_vat("B12345674", name="WooCommerce clinic")
        second = self._customer_with_vat("ESB12345674", name="WooCommerce surgery")
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
            meta_data=self._nif(FIXTURE_CIF),
        )
        with self.assertRaises(ValidationError) as error:
            self._import_order(order)
        self.assertEqual(
            error.exception.args[0],
            "2 contacts have the Tax ID ESB12345674, which must belong to one "
            "contact only:" + self._contact_lines(first, second),
        )

    def test_three_contacts_with_the_nif_are_all_named(self):
        first = self._customer_with_vat("B12345674", name="WooCommerce clinic")
        second = self._customer_with_vat("ESB12345674", name="WooCommerce surgery")
        third = self._customer_with_vat("B-12345674", name="WooCommerce practice")
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
            meta_data=self._nif(FIXTURE_CIF),
        )
        with self.assertRaises(ValidationError) as error:
            self._import_order(order)
        self.assertEqual(
            error.exception.args[0],
            "3 contacts have the Tax ID ESB12345674, which must belong to one "
            "contact only:" + self._contact_lines(first, second, third),
        )

    def test_contact_under_a_company_gives_the_company(self):
        company = self._customer_with_vat("ESB12345674")
        # Odoo gives a company's contacts its VAT number
        person = self.env["res.partner"].create(
            {"name": "WooCommerce contact person", "parent_id": company.id}
        )
        self.assertEqual(person.vat, "ESB12345674")
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
            meta_data=self._nif(FIXTURE_CIF),
        )
        self._import_order(order)
        self.assertEqual(self._imported_order(order).partner_id, company)

    def test_customer_found_without_an_address_keeps_none(self):
        customer = self.env["res.partner"].create(
            {"name": "WooCommerce clinic", "vat": "ESB12345674"}
        )
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
            meta_data=self._nif(FIXTURE_CIF),
        )
        self._import_order(order)
        self.assertEqual(self._imported_order(order).partner_id, customer)
        self.assertFalse(customer.street)
        self.assertFalse(customer.city)
        self.assertFalse(customer.country_id)

    def test_order_without_nif_finds_the_customer_by_name(self):
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
        self.assertEqual(self._imported_order(order).partner_id, customer)

    def test_order_without_nif_gets_a_new_customer_without_vat(self):
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
        )
        self._import_order(order)
        customer = self._imported_order(order).partner_id
        self.assertEqual(customer.name, "WooCommerce buyer")
        self.assertFalse(customer.vat)

    def test_re_import_takes_the_customer_from_its_bound_address(self):
        order = self._shop_order(
            30001,
            billing=self._address_block(
                "WooCommerce", "buyer", email="buyer@example.com"
            ),
            shipping=self._address_block("WooCommerce", "buyer"),
            meta_data=self._nif(FIXTURE_NIF),
        )
        self._import_order(order)
        sale = self._imported_order(order)
        # A second contact with the same NIF, as a search would also find
        self._customer_with_vat("12345678Z", name="WooCommerce namesake")
        contacts = self._all_contacts()
        result = self._import_order(order)
        self.assertEqual(
            result,
            "The Order %s is already imported -> Update not allowed"
            % sale.display_name,
        )
        self.assertEqual(self._all_contacts(), contacts)
