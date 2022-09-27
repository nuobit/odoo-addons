# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Prorate Asset",
    "summary": "This module add prorate fields on asset",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "account_asset_management_extension",
        "l10n_es_aeat_vat_special_prorrate",
    ],
    "data": ["views/account_asset.xml"],
}
