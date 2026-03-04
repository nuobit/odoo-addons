# Copyright NuoBiT Solutions SL - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "AEAT 303 - Special Prorate Regularization Capital Asset legacy",
    "summary": "This module extends Special Prorate Regularization Capital Asset "
    "to include old assets",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_aeat_mod303_special_prorate_regularization_capital_asset",
    ],
    "data": [
        "views/aeat_tax_line_view.xml",
    ],
}
