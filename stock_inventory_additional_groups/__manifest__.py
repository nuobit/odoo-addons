# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock inventory additional groups",
    "summary": "This module adds adittional permission groups on inventory module",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "category": "Warehouse",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "stock",
    ],
    "data": ["security/stock_security.xml", "views/stock_inventory_views.xml"],
    "installable": True,
}
