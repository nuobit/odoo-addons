# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=C7902
from openupgradelib import openupgrade

_field_renames = [
    (
        "res.company",
        "res_company",
        "default_invoice_batch_sending_email_template_id",
        "invoice_batch_sending_email_template_id",
    )
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.lift_constraints(env.cr, "account_invoice", "invoice_batch_id")
    openupgrade.rename_fields(env, _field_renames)
