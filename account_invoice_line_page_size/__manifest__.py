# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Invoice line page size",
    "version": "12.0.1.0.0",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Sale",
    "website": "https://github.com/OCA/pms",
    "summary": "This module sets the page size of the " "invoices lines to 200",
    "depends": [
        "account",
    ],
    "data": [
        "views/account_invoice_views.xml",
    ],
    "installable": True,
}
