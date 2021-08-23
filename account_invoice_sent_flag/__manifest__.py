# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account invoice sent flag",
    "description": 'This module shows the "sent" flag on invoices and adds a filter',
    "category": "Accounting",
    "version": "11.0.1.0.0",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "depends": ["account"],
    "data": [
        "views/account_invoice_views.xml",
    ],
    "installable": True,
}
