# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock Restrict Lot Name",
    "summary": "This module restrict modification of lots/serial numbers names "
    "to specific user groups",
    "author": "NuoBiT Solutions, S.L.",
    "category": "Inventory/Inventory",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": ["stock"],
    "data": [
        "security/stock_restrict_lot_name_security.xml",
    ],
}
