# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=C7902
from openupgradelib import openupgrade


def update_invoice_move_map(env):
    # field invoice_id
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_asset
        ADD COLUMN move_id integer""",
    )
    openupgrade.lift_constraints(env.cr, "account_asset", "invoice_id")
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_asset asset
        SET move_id = am.id
        FROM account_move am
        WHERE asset.invoice_id = am.old_invoice_id""",
    )
    # field invoice_line_id
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_asset
        ADD COLUMN move_line_id integer""",
    )
    openupgrade.lift_constraints(env.cr, "account_asset", "invoice_line_id")
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_asset asset
        SET move_line_id = aml.id
        FROM account_move_line aml
        WHERE asset.invoice_line_id = aml.old_invoice_line_id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    update_invoice_move_map(env)
