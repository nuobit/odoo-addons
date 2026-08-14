# Copyright NuoBiT Solutions SL - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Prorate Asset",
    "summary": "This module add prorate fields on asset",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "account_asset_management_extension",
        "l10n_es_aeat_vat_special_prorrate",
        "l10n_es_asset_extension",
    ],
    "data": ["views/account_asset.xml"],
}
