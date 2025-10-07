# Copyright NuoBiT Solutions- Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock Restrict Lot Name",
    "summary": "This module restrict modification of lots/serial numbers names "
    "to specific user groups",
    "author": "NuoBiT Solutions SL",
    "category": "Inventory/Inventory",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": ["stock"],
    "data": [
        "security/stock_restrict_lot_name_security.xml",
    ],
}
