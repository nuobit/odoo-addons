# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock Picking Date Filter",
    "version": "16.0.1.0.1",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Stock",
    "website": "https://github.com/nuobit/odoo-addons",
    "summary": "This module adds date filters to stock picking tree view",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_picking_views.xml",
    ],
    "installable": True,
}
