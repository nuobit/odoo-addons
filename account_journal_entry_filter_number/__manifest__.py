# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT 2025 - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Journal Entry Filter Number",
    "summary": "This module adds a new filter on Journal Entry tree view "
    "to filter only by Number",
    "category": "Accounting",
    "version": "16.0.1.0.0",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions SL",
    "depends": ["account"],
    "data": [
        "views/account_move_view.xml",
    ],
}
