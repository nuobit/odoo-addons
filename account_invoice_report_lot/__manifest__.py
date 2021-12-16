# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Invoice report lot",
    "version": "12.0.1.0.3",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Invoicing Management",
    "website": "https://github.com/nuobit/odoo-addons",
    "summary": "This module adds a lot/serial number on lines of invoice reports",
    "depends": [
        "stock_picking_invoice_link",
    ],
    "data": ["views/report_invoice.xml"],
    "installable": True,
}
