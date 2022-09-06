# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "AEAT 303 - Special Prorate Regularization",
    "summary": "This module allows to regularize prorate differences on 303 report",
    "version": "14.0.1.0.0",
    "category": "Acconting",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_aeat_mod303",
        "l10n_es_aeat_vat_special_prorrate",
        "account_asset_management",
        "account_asset_invoice_line_link",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/tax_code_map_mod303_data.xml",
        "views/mod303_views.xml",
        "views/account_asset.xml",
        "views/account_asset_profile_views.xml",
        "views/aeat_vat_special_prorrate_investment_capital_asset_type_view.xml",
    ],
}
