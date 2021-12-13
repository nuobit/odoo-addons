# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock REST",
    "author": "NuoBiT Solutions, S.L.",
    "category": "Stock",
    "version": "11.0.1.0.7",
    "license": "AGPL-3",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": ["stock", "connector_sage", "base_rest"],
    "data": [
        "views/stock_picking_views.xml",
    ],
    "installable": True,
}
