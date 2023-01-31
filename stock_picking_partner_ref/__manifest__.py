# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock picking partner reference",
    "summary": "Adds a partner reference on picking",
    "author": "NuoBiT Solutions",
    "maintainers": ["eantones"],
    "category": "Warehouse",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_picking_views.xml",
    ],
    "installable": True,
}
