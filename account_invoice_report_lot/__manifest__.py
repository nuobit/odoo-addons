# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Invoice report lot",
    "version": "17.0.0.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Invoicing Management",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "summary": "This module adds a lot/serial number on lines of invoice reports",
    "depends": [
        "stock_picking_invoice_link",
    ],
    "data": ["views/report_invoice.xml"],
}
