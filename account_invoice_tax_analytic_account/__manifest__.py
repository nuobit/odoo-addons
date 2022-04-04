# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account tax invoice analytic",
    "summary": "This module allows to add an analytic account "
    "and analytic tags manually to invoice taxes.",
    "version": "12.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": ["account"],
    "data": [
        "views/account_invoice_view.xml",
    ],
    "installable": True,
}
