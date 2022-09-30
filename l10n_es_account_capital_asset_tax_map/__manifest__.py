# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Capital Asset Tax Map",
    "summary": "This module adds l10n_es data to capital assets tax map",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_special_prorate",
        "l10n_es_account_capital_asset",
    ],
    "data": [
        "data/account_capital_asset_map_tax_data.xml",
    ],
    "installable": True,
}
