from odoo.tests import Form

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractSii(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_model = cls.env["res.company"]
        cls.contract_model = cls.env["contract.contract"]
        cls.aml_model = cls.env["account.move.line"]
        cls.registration_keys_model = cls.env["aeat.sii.mapping.registration.keys"]
        cls.env.company.write(
            {
                "sii_enabled": True,
                "sii_test": True,
            }
        )

    def test_contract_sale_sii(self):
        contract_sale_form = Form(
            self.contract_model.with_context(
                is_contract=True, default_contract_type="sale"
            )
        )
        contract_sale_form.name = "Test Contract"
        contract_sale_form.partner_id = self.partner
        contract_sale_form.pricelist_id = self.partner.property_product_pricelist
        contract_sale_form.recurring_interval = 1
        contract_sale_form.recurring_rule_type = "monthly"
        sale_keys = self.registration_keys_model.search([("type", "=", "sale")])
        contract_sale_form.sii_registration_key = sale_keys[0]
        contract_sale_form.sii_registration_key_additional1 = sale_keys[0]
        contract_sale_form.sii_registration_key_additional2 = sale_keys[0]
        contract_sale_form.sii_property_cadastrial_code = "12345"
        contract_sale_form.recurring_interval = 1
        line_form = contract_sale_form.contract_line_ids.new()
        line_form.product_id = self.product_1
        line_form.name = "Services from #START# to #END#"
        line_form.quantity = 1
        line_form.price_unit = 100
        line_form.discount = 50
        line_form.recurring_rule_type = "monthly"
        line_form.recurring_interval = 1
        line_form.date_start = "2018-02-15"
        line_form.recurring_next_date = "2018-02-22"
        line_form.save()
        self.contract_sale_ssi = contract_sale_form.save()
        self.contract_sale_ssi._compute_recurring_next_date()
        self.contract_sale_ssi.recurring_create_invoice()
        invoices = self.aml_model.search(
            [
                (
                    "contract_line_id",
                    "in",
                    self.contract_sale_ssi.contract_line_ids.ids,
                )
            ]
        ).mapped("move_id")
        self.assertEqual(
            invoices.mapped("sii_registration_key").ids,
            self.contract_sale_ssi.sii_registration_key.ids,
        )
        self.assertEqual(
            invoices.mapped("sii_registration_key_additional1").ids,
            self.contract_sale_ssi.sii_registration_key_additional1.ids,
        )
        self.assertEqual(
            invoices.mapped("sii_registration_key_additional2").ids,
            self.contract_sale_ssi.sii_registration_key_additional2.ids,
        )
        self.assertEqual(
            invoices.mapped("sii_property_location")[0],
            self.contract_sale_ssi.sii_property_location,
        )
        self.assertEqual(
            invoices.mapped("sii_property_cadastrial_code")[0],
            self.contract_sale_ssi.sii_property_cadastrial_code,
        )

    def test_contract_purchase_sii(self):
        contract_purchase_form = Form(
            self.contract_model.with_context(
                is_contract=True, default_contract_type="purchase"
            )
        )
        contract_purchase_form.name = "Test Contract"
        contract_purchase_form.partner_id = self.partner
        contract_purchase_form.pricelist_id = self.partner.property_product_pricelist
        sale_keys = self.registration_keys_model.search([("type", "=", "purchase")])
        contract_purchase_form.sii_registration_key = sale_keys[0]
        contract_purchase_form.sii_registration_key_additional1 = sale_keys[0]
        contract_purchase_form.sii_registration_key_additional2 = sale_keys[0]
        contract_purchase_form.sii_property_location = "1"
        contract_purchase_form.recurring_rule_type = "monthly"
        line_form = contract_purchase_form.contract_line_ids.new()
        line_form.product_id = self.product_1
        line_form.name = "Services from #START# to #END#"
        line_form.quantity = 1
        line_form.price_unit = 100
        line_form.discount = 50
        line_form.recurring_rule_type = "monthly"
        line_form.recurring_interval = 1
        line_form.date_start = "2018-02-15"
        line_form.recurring_next_date = "2018-02-22"
        line_form.save()
        self.contract_purchase_ssi = contract_purchase_form.save()
        self.contract_purchase_ssi._compute_recurring_next_date()
        self.contract_purchase_ssi.recurring_create_invoice()
        invoices = self.aml_model.search(
            [
                (
                    "contract_line_id",
                    "in",
                    self.contract_purchase_ssi.contract_line_ids.ids,
                )
            ]
        ).mapped("move_id")
        self.assertEqual(
            invoices.mapped("sii_registration_key").ids,
            self.contract_purchase_ssi.sii_registration_key.ids,
        )
        self.assertEqual(
            invoices.mapped("sii_registration_key_additional1").ids,
            self.contract_purchase_ssi.sii_registration_key_additional1.ids,
        )
        self.assertEqual(
            invoices.mapped("sii_registration_key_additional2").ids,
            self.contract_purchase_ssi.sii_registration_key_additional2.ids,
        )
