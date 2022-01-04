from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractLine(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.aml_obj = cls.env["account.move.line"]

    def test_contract_comment(self):
        self.contract2.write({"comment": "Some Information"})
        self.contract2.recurring_create_invoice()
        invoices = self.aml_obj.search(
            [
                (
                    "contract_line_id",
                    "in",
                    self.contract2.contract_line_ids.ids,
                )
            ]
        ).mapped("move_id")
        self.assertEqual([self.contract2.comment], invoices.mapped("narration"))
        self.contract3.recurring_create_invoice()
        invoices = self.aml_obj.search(
            [
                (
                    "contract_line_id",
                    "in",
                    self.contract3.contract_line_ids.ids,
                )
            ]
        ).mapped("move_id")
        self.assertEqual([self.contract3.comment], invoices.mapped("narration"))
