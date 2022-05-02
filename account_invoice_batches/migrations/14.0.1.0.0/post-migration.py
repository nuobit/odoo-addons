# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=C7902
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET invoice_batch_id = ai.invoice_batch_id,
            invoice_batch_sending_method = ai.invoice_batch_sending_method,
            invoice_batch_email_partner_id = ai.invoice_batch_email_partner_id
        FROM account_invoice ai
        WHERE am.old_invoice_id = ai.id AND ai.invoice_batch_id IS NOT NULL
        """,
    )
    openupgrade.load_data(
        env.cr, "account_invoice_batches", "migrations/14.0.1.0.0/noupdate_changes.xml"
    )
