# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Contract comment",
    "summary": "This module adds a comment field in the contract "
    "and propagates it to the narration field of the invoice",
    "version": "17.0.0.0.0",
    "category": "Contract Management",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "contract",
    ],
    "data": [
        "views/contract_view.xml",
    ],
}
