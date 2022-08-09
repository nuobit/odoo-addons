# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Special Prorate Reguilarization",
    "summary": "This module allows to regularize prorate differences",
    "version": "14.0.1.0.0",
    "category": "Sales",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_aeat_mod303",
        "l10n_es_aeat_vat_special_prorrate",
        "account_asset_management",
    ],
    "data": [
        "data/tax_code_map_mod303_data.xml",
        "views/mod303_views.xml",
        "views/account_asset.xml",
        "views/product_category_views.xml",
    ],
}
