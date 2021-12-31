from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractLine(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax_obj = cls.env["account.tax"]
        cls.aml_obj = cls.env["account.move.line"]
        cls.tax_customer = cls.tax_obj.create(
            {
                "name": "Customer Tax 20%",
                "type_tax_use": "sale",
                "amount": 20,
                "tax_exigibility": "on_invoice",
            }
        )
        cls.tax_supplier = cls.tax_obj.create(
            {
                "name": "Supplier Tax 10%",
                "type_tax_use": "purchase",
                "amount": 10,
                "tax_exigibility": "on_invoice",
            }
        )

    def test_contract_line_tax_ids(self):
        for line in self.contract2.contract_line_ids:
            line.write({"tax_ids": [(6, 0, self.tax_customer.ids)]})
        self.contract2.recurring_create_invoice()
        for line in self.contract2.contract_line_ids:
            invoice_lines = self.aml_obj.search(
                [
                    (
                        "contract_line_id",
                        "=",
                        line.id,
                    )
                ]
            )
            self.assertEqual(self.tax_customer.ids, invoice_lines.mapped("tax_ids").ids)
        for line in self.contract3.contract_line_ids:
            line.write({"tax_ids": [(6, 0, self.tax_supplier.ids)]})
        self.contract3.recurring_create_invoice()
        for line in self.contract3.contract_line_ids:
            invoice_lines = self.aml_obj.search(
                [
                    (
                        "contract_line_id",
                        "=",
                        line.id,
                    )
                ]
            )
            self.assertEqual(self.tax_supplier.ids, invoice_lines.mapped("tax_ids").ids)
