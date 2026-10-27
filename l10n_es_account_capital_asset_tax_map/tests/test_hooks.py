# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.modules.migration import load_script
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

from ..hooks import post_init_hook


@tagged("post_install", "-at_install")
class TestHooks(AccountTestInvoicingCommon):
    @classmethod
    @AccountTestInvoicingCommon.setup_country("es")
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.company_data["company"]
        cls.chart_template = cls.env["account.chart.template"].with_company(cls.company)
        cls.map_tax_domain = [("company_id", "=", cls.company.id)]
        # The map as l10n_es_account_capital_asset leaves it when it migrates
        # from 14.0: empty
        cls.env["l10n.es.account.capital.asset.map.tax"].search(
            cls.map_tax_domain
        ).unlink()

    def test_post_init_hook_xmlids(self):
        post_init_hook(self.env(su=True))
        map_tax = self.chart_template.ref("account_tax_template_p_iva4_bc_bi")
        self.assertEqual(
            map_tax.tax_src_id,
            self.chart_template.ref("account_tax_template_p_iva4_bc"),
        )
        self.assertEqual(
            map_tax.tax_dest_id,
            self.chart_template.ref("account_tax_template_p_iva4_bi"),
        )
        self.assertEqual(
            self.env["l10n.es.account.capital.asset.map.tax"].search_count(
                self.map_tax_domain
            ),
            9,
        )

    def test_post_init_hook_reload(self):
        post_init_hook(self.env(su=True))
        self.env(su=True)["account.chart.template"].try_loading(
            self.company.chart_template, self.company
        )
        self.assertEqual(
            self.env["l10n.es.account.capital.asset.map.tax"].search_count(
                [
                    ("company_id", "=", self.company.id),
                    (
                        "tax_src_id",
                        "=",
                        self.chart_template.ref("account_tax_template_p_iva4_bc").id,
                    ),
                    (
                        "tax_dest_id",
                        "=",
                        self.chart_template.ref("account_tax_template_p_iva4_bi").id,
                    ),
                ]
            ),
            1,
        )

    def test_post_init_hook_row_without_xmlid(self):
        map_tax = self.env["l10n.es.account.capital.asset.map.tax"].create(
            {
                "company_id": self.company.id,
                "tax_src_id": self.chart_template.ref(
                    "account_tax_template_p_iva4_bc"
                ).id,
                "tax_dest_id": self.chart_template.ref(
                    "account_tax_template_p_iva4_bi"
                ).id,
            }
        )
        post_init_hook(self.env(su=True))
        self.assertEqual(
            self.chart_template.ref("account_tax_template_p_iva4_bc_bi"), map_tax
        )
        self.assertEqual(
            self.env["l10n.es.account.capital.asset.map.tax"].search_count(
                self.map_tax_domain
            ),
            9,
        )

    def test_post_init_hook_changed_row(self):
        post_init_hook(self.env(su=True))
        map_tax = self.chart_template.ref("account_tax_template_p_iva4_bc_bi")
        map_tax.tax_dest_id = self.chart_template.ref("account_tax_template_p_iva10_bi")
        post_init_hook(self.env(su=True))
        self.assertEqual(
            map_tax.tax_dest_id,
            self.chart_template.ref("account_tax_template_p_iva10_bi"),
        )
        self.assertEqual(
            self.env["l10n.es.account.capital.asset.map.tax"].search_count(
                self.map_tax_domain
            ),
            9,
        )

    def test_post_init_hook_missing_tax(self):
        self.env(su=True)["ir.model.data"].search(
            [
                ("module", "=", "account"),
                ("name", "=", f"{self.company.id}_account_tax_template_p_iva4_bc"),
            ]
        ).unlink()
        post_init_hook(self.env(su=True))
        self.assertFalse(
            self.chart_template.ref(
                "account_tax_template_p_iva4_bc_bi", raise_if_not_found=False
            )
        )
        self.assertEqual(
            self.env["l10n.es.account.capital.asset.map.tax"].search_count(
                self.map_tax_domain
            ),
            8,
        )

    def test_post_migration(self):
        post_migration = load_script(
            "l10n_es_account_capital_asset_tax_map"
            "/migrations/18.0.1.0.3/post-migration.py",
            "post_migration",
        )
        post_migration.migrate(self.env.cr, "14.0.1.0.0")
        self.assertEqual(
            self.env["l10n.es.account.capital.asset.map.tax"].search_count(
                self.map_tax_domain
            ),
            9,
        )
