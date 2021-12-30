# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Contract comment",
    "summary": "This module adds a comment field in the contract and propagates it to the comment field of the invoice",
    "version": "11.0.0.1.0",
    "category": "Contract Management",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "contract",
    ],
    "data": [
        "views/account_analytic_contract_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
