# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock REST",
    "author": "NuoBiT Solutions SL",
    "category": "Stock",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "stock_location_code",
        "base_rest",
        "account_asset_management",
        "stock_picking_partner_ref",
        "stock_inventory",
    ],
    "data": [
        "views/stock_picking_views.xml",
    ],
}
