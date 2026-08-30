# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

_MODULE = "l10n_es_aeat_mod303_special_prorate_regularization_capital_asset_legacy"

_field_renames = [
    (
        "l10n.es.aeat.tax.line",
        "l10n_es_aeat_tax_line",
        "asset_ids",
        "legacy_asset_ids",
    ),
]

_xmlid_renames = [
    (
        "%s.field_l10n_es_aeat_tax_line__asset_ids" % _MODULE,
        "%s.field_l10n_es_aeat_tax_line__legacy_asset_ids" % _MODULE,
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
