# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock REST",
    "author": "NuoBiT Solutions, S.L.",
    "category": "Stock",
    "version": "14.0.1.1.1",
    "license": "AGPL-3",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "stock_location_code",
        "connector_sage",
        "base_rest",
        "account_asset_management",
        "stock_picking_partner_ref",
    ],
    "data": [
        "views/stock_picking_views.xml",
    ],
    "installable": True,
}
