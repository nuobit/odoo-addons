# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock move line sale order",
    "summary": "This module adds field sale order to stock move line views",
    "version": "12.0.1.0.1",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Custom",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "sale_stock",
    ],
    "data": [
        "views/stock_move_line_views.xml",
    ],
    "installable": True,
}
