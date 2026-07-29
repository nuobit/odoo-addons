# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.osv import expression
from odoo.tests.common import SavepointCase


class TestVatTaxSearch(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ARRANGE
        account_type_asset = cls.env.ref("account.data_account_type_fixed_assets")
        account_type_expense = cls.env.ref("account.data_account_type_expenses")
        account_asset = cls.env["account.account"].create(
            {
                "name": "Test Fixed Asset",
                "code": "TEST220000",
                "user_type_id": account_type_asset.id,
            }
        )
        account_depreciation = cls.env["account.account"].create(
            {
                "name": "Test Depreciation",
                "code": "TEST281000",
                "user_type_id": account_type_asset.id,
            }
        )
        account_expense = cls.env["account.account"].create(
            {
                "name": "Test Depreciation Expense",
                "code": "TEST681000",
                "user_type_id": account_type_expense.id,
            }
        )
        journal = cls.env["account.journal"].create(
            {"name": "Test Assets Journal", "code": "TASSET", "type": "general"}
        )
        profile = cls.env["account.asset.profile"].create(
            {
                "name": "Test Asset Profile",
                "journal_id": journal.id,
                "account_asset_id": account_asset.id,
                "account_depreciation_id": account_depreciation.id,
                "account_expense_depreciation_id": account_expense.id,
            }
        )
        vat_group = cls.env["account.tax.group"].create(
            {"name": "Test VAT Group", "is_vat": True}
        )
        other_group = cls.env["account.tax.group"].create(
            {"name": "Test Non-VAT Group", "is_vat": False}
        )
        # modules outside this module's dependency tree may constrain taxes
        # further when co-installed in a shared test database (e.g.
        # account_asset_tax_consistency requires apply_to_asset == "always")
        extra_tax_vals = {}
        if "apply_to_asset" in cls.env["account.tax"]._fields:
            extra_tax_vals["apply_to_asset"] = "always"
        cls.vat_tax = cls.env["account.tax"].create(
            {
                "name": "Test VAT 21%",
                "amount": 21.0,
                "type_tax_use": "purchase",
                "tax_group_id": vat_group.id,
                **extra_tax_vals,
            }
        )
        cls.other_tax = cls.env["account.tax"].create(
            {
                "name": "Test Surcharge 5.2%",
                "amount": 5.2,
                "type_tax_use": "purchase",
                "tax_group_id": other_group.id,
                **extra_tax_vals,
            }
        )
        cls.asset = cls.env["account.asset"].create(
            {
                "name": "Test Asset",
                "profile_id": profile.id,
                "purchase_value": 1000.0,
                "date_start": "2021-01-01",
                "quantity": 1.0,
                "tax_ids": [(6, 0, (cls.vat_tax + cls.other_tax).ids)],
            }
        )
        cls.asset_no_vat = cls.env["account.asset"].create(
            {
                "name": "Test Asset without VAT",
                "profile_id": profile.id,
                "purchase_value": 500.0,
                "date_start": "2021-01-01",
                "quantity": 1.0,
                "tax_ids": [(6, 0, cls.other_tax.ids)],
            }
        )

    def test_compute_vat_tax(self):
        self.assertEqual(self.asset.vat_tax_id, self.vat_tax)
        self.assertFalse(self.asset_no_vat.vat_tax_id)

    def test_search_by_vat_tax(self):
        assets = self.env["account.asset"].search(
            [("vat_tax_id", "in", self.vat_tax.ids)]
        )
        self.assertIn(self.asset, assets)
        self.assertNotIn(self.asset_no_vat, assets)

    def test_search_by_non_vat_tax_matches_nothing(self):
        domain = self.env["account.asset"]._search_vat_tax_id("in", self.other_tax.ids)
        self.assertEqual(domain, expression.FALSE_DOMAIN)
        self.assertFalse(
            self.env["account.asset"].search([("vat_tax_id", "in", self.other_tax.ids)])
        )

    def test_search_unset(self):
        assets = self.env["account.asset"].search([("vat_tax_id", "=", False)])
        self.assertIn(self.asset_no_vat, assets)
        self.assertNotIn(self.asset, assets)
        assets = self.env["account.asset"].search([("vat_tax_id", "!=", False)])
        self.assertIn(self.asset, assets)
        self.assertNotIn(self.asset_no_vat, assets)

    def test_search_negative(self):
        assets = self.env["account.asset"].search(
            [("vat_tax_id", "not in", self.vat_tax.ids)]
        )
        self.assertNotIn(self.asset, assets)
        self.assertIn(self.asset_no_vat, assets)

    def test_search_empty_value(self):
        Asset = self.env["account.asset"]
        self.assertEqual(Asset._search_vat_tax_id("in", []), expression.FALSE_DOMAIN)
        self.assertEqual(Asset._search_vat_tax_id("not in", []), expression.TRUE_DOMAIN)

    def test_search_unsupported_operator(self):
        with self.assertRaises(NotImplementedError):
            self.env["account.asset"]._search_vat_tax_id("ilike", "vat")

    def test_tax_write_triggers_recompute(self):
        self.assertAlmostEqual(self.asset.vat_tax_amount, 210.0, places=2)
        self.vat_tax.amount = 10.0
        self.assertAlmostEqual(self.asset.vat_tax_amount, 100.0, places=2)

    def test_tax_unlink_no_degradation(self):
        throwaway = self.env["account.tax"].create(
            {
                "name": "Test Throwaway",
                "amount": 1.0,
                "type_tax_use": "purchase",
            }
        )
        throwaway.unlink()
        self.assertEqual(self.asset.vat_tax_id, self.vat_tax)
