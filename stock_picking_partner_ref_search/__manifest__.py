# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock picking partner ref search",
    "summary": "This module adds partner ref in the stock "
    "picking to search by this field",
    "version": "12.0.1.0.1",
    "author": "NuoBiT Solutions, S.L., Kilian Niubo",
    "license": "AGPL-3",
    "category": "Custom",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "stock",
        "sale",
        "purchase",
    ],
    "data": [
        "views/stock_picking_views.xml",
    ],
    "installable": True,
}
