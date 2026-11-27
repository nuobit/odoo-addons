# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account invoice sent flag",
    "summary": 'This module shows the "is_move_sent" flag on invoices and adds a filter',
    "category": "Accounting",
    "version": "16.0.1.0.0",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions SL",
    "depends": ["account"],
    "data": [
        "views/account_invoice_views.xml",
    ],
}
