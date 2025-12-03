# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Bijaya Kumal <bkumal@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Asset Tax Consistency",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Invoicing Management",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "summary": "This module checks the consistency of taxes when an asset is created."
    "reports defined on invoice services.",
    "depends": [
        "account_asset_management_extension",
    ],
    "data": [
        "views/account_tax_views.xml",
    ],
}
