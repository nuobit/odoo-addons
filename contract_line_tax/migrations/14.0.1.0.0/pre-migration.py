# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=C7902
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(
        env.cr,
        {
            "account_analytic_contract_line_account_tax_rel": [
                ("account_analytic_contract_line_id", "contract_line_id")
            ]
        },
    )
    openupgrade.rename_tables(
        env.cr,
        [
            (
                "account_analytic_contract_line_account_tax_rel",
                "account_tax_contract_line_rel",
            )
        ],
    )
