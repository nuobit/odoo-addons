# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "L10n ES Extension - Account Asset Tax Consistency",
    "summary": "Set asset applicability on l10n_es_extension tax templates",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_extension",
        "account_asset_tax_consistency",
    ],
    "data": [
        "data/account_tax_template_data.xml",
    ],
    "auto_install": True,
}
