# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

from odoo.tools.sql import column_exists, table_exists

_column_renames = {
    "account_asset_profile": [
        ("capital_asset_type_id", "default_capital_asset_type_id"),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    if column_exists(env.cr, "account_asset_profile", "capital_asset_type_id"):
        openupgrade.rename_columns(env.cr, _column_renames)
    if table_exists(
        env.cr, "l10n_es_account_capital_asset_map_tax"
    ) and not column_exists(
        env.cr, "l10n_es_account_capital_asset_map_tax", "company_id"
    ):
        # Template-era schema (<=16): tax_src_id/tax_dest_id reference
        # account_tax_template, which no longer exists, so the ids cannot
        # satisfy the account_tax FK the 18.0 model declares and the registry
        # re-creates right after this script. The rows carry nothing worth
        # converting: the 18.0 map content is reseeded per company by
        # l10n_es_account_capital_asset_tax_map's idempotent post_init_hook.
        openupgrade.logged_query(
            env.cr, "DELETE FROM l10n_es_account_capital_asset_map_tax"
        )
