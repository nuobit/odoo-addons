# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT 2025 - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Asset Tax Consistency",
    "version": "16.0.1.0.1",
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
        "views/account_tax_template_views.xml",
    ],
}
