# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

from odoo.tools.sql import column_exists

_column_renames = {
    "capital_asset_prorate_regularization": [
        ("sii_state", "aeat_state"),
        ("sii_header_sent", "aeat_header_sent"),
        ("sii_content_sent", "aeat_content_sent"),
        ("sii_send_error", "aeat_send_error"),
        ("sii_send_failed", "aeat_send_failed"),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    if column_exists(env.cr, "capital_asset_prorate_regularization", "sii_state"):
        openupgrade.rename_columns(env.cr, _column_renames)
