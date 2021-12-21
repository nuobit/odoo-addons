# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock picking employee",
    "summary": "Adds employees on picking",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "category": "Warehouse",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": ["stock", "hr"],
    "data": [
        "views/stock_picking_views.xml",
    ],
    "installable": True,
}
