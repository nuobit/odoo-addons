# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Capital Asset Data",
    "summary": "This module adds l10n_es data to special prorate capital "
    "assets tax map, asset category types and threshold amount",
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
        "data/account_capital_asset_type_data.xml",
        "data/ir_config_parameter.xml",
    ],
    "installable": True,
}
