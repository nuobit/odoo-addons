# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

from odoo.tools.sql import column_exists

_column_renames = {
    "account_asset_profile": [
        ("capital_asset_type_id", "default_capital_asset_type_id"),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    if column_exists(env.cr, "account_asset_profile", "capital_asset_type_id"):
        openupgrade.rename_columns(env.cr, _column_renames)
