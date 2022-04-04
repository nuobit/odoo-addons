# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=C7902
from openupgradelib import openupgrade


def update_invoice_move_map(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET origin_analytic_account_id = ait.origin_account_analytic_id
        FROM account_invoice_tax ait
        WHERE aml.old_invoice_tax_id = ait.id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_move_origin_analytic_tag_rel (tag_id, move_id)
        SELECT invoice_rel.tag_id, aml.id
        FROM account_invoice_origin_analytic_tag_rel invoice_rel
        JOIN account_move_line aml ON aml.old_invoice_tax_id = invoice_rel.invoice_id
        ON CONFLICT DO NOTHING""",
    )
    openupgrade.remove_tables_fks(env.cr, ["account_invoice_origin_analytic_tag_rel"])


@openupgrade.migrate()
def migrate(env, version):
    update_invoice_move_map(env)
