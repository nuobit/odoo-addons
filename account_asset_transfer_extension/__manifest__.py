# Copyright NuoBiT Solutions SL - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Asset Transfer Extension",
    "summary": "This module extends account_asset_transfer ",
    "author": "NuoBiT Solutions SL",
    "category": "Accounting",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": ["account_asset_transfer"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_asset_views.xml",
        "wizards/account_asset_transfer_revert.xml",
    ],
}
