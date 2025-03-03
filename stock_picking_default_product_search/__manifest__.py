# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT 2025 - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


{
    "name": "Stock Picking Default Product Search",
    "summary": "This module allows searching for product on stock picking view",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL, Eric Antones",
    "license": "AGPL-3",
    "category": "Inventory",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_picking_views.xml",
    ],
    "installable": True,
}
