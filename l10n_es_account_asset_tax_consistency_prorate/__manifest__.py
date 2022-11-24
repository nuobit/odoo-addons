# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "L10n ES - Account Tax Consistency Prorate",
    "summary": "This module adds in taxes of l10n_es_special_prorate "
    "data account asset tax consistency selection field",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_special_prorate",
        "account_asset_tax_consistency",
    ],
    "data": [
        "data/l10n_es_account_asset_tax_consistency_data.xml",
    ],
    "installable": True,
    "auto_install": True,
}
