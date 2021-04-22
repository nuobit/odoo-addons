# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account tax invoice analytic",
    "description": "This module allows to add analytic account manually on invoice taxes.",
    "version": "11.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/OCA/pms",
    "depends": ["account"],
    "data": [
        "views/account_invoice_view.xml",
    ],
    "installable": True,
}
