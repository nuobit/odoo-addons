# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "AEAT 303 - Special Prorate Regularization Capital Asset",
    "summary": "This module allows to regularize capital assets "
    "prorate differences on 303 report",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_account_capital_asset",
        "l10n_es_aeat_mod303_special_prorate_regularization",
        "l10n_es_aeat_prorate_asset",
    ],
    "data": [
        "data/ir_config_parameter.xml",
        "security/ir.model.access.csv",
        "views/mod303_views.xml",
        "views/account_asset.xml",
        "views/res_config_settings_views.xml",
    ],
}
