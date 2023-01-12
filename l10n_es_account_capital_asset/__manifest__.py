# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Capital Asset",
    "summary": "This module adds mapping for capital assets taxes, capital assets"
    " category types and threshold amount on res_config",
    "version": "14.0.1.0.2",
    "category": "Accounting",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_asset_extension",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/account_capital_asset_type_data.xml",
        "data/ir_config_parameter.xml",
        "views/account_asset.xml",
        "views/account_asset_profile_views.xml",
        "views/account_capital_asset_map_tax_views.xml",
        "views/account_capital_asset_type_view.xml",
        "views/res_company_view.xml",
        "views/res_config_settings_views.xml",
    ],
}
