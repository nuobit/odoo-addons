# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Asset Transfer Extension",
    "summary": "This module extends account_asset_transfer ",
    "author": "NuoBiT Solutions, S.L.",
    "category": "Accounting",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": ["account_asset_transfer"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_asset.xml",
        "wizard/account_asset_transfer_revert.xml",
    ],
}
