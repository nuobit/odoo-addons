# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountMove(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax_purchase_c = cls.tax_purchase_b.copy()
        cls.asset_profile = cls.env["account.asset.profile"].create(
            {
                "account_expense_depreciation_id": cls.company_data[
                    "default_account_expense"
                ].id,
                "account_asset_id": cls.company_data["default_account_assets"].id,
                "account_depreciation_id": cls.company_data[
                    "default_account_assets"
                ].id,
                "journal_id": cls.company_data["default_journal_purchase"].id,
                "name": "Hardware - 3 Years",
                "method_time": "year",
                "method_number": 3,
                "method_period": "year",
            }
        )

    def test_asset_from_invoice_taxes(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "invoice_date": fields.Date.context_today(self.env.user),
                "partner_id": self.partner_a.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "Laptop",
                            "product_id": self.product_a.id,
                            "price_unit": 2000.00,
                            "quantity": 1,
                            "asset_profile_id": self.asset_profile.id,
                            "tax_ids": [
                                Command.set(
                                    [self.tax_purchase_b.id, self.tax_purchase_c.id]
                                )
                            ],
                        }
                    ),
                ],
            }
        )
        invoice.action_post()
        asset = invoice.invoice_line_ids.asset_id
        self.assertEqual(len(asset), 1)
        self.assertEqual(asset.tax_ids, self.tax_purchase_b + self.tax_purchase_c)
