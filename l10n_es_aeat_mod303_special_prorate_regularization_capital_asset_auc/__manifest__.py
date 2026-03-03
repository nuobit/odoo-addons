# Copyright NuoBiT Solutions SL - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "AEAT 303 - Special Prorate Regularization Capital Asset AUC",
    "summary": "This module allows to regularize transferred capital assets "
    "prorate differences on 303 report",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_aeat_mod303_special_prorate_regularization_capital_asset",
        "account_asset_transfer_extension",
    ],
    "data": [
        "views/account_asset_views.xml",
    ],
    "auto_install": True,
}
