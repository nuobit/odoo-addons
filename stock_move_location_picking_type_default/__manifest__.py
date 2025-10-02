# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Move Stock Location Picking Type Default",
    "summary": "This module allows defining a default picking type "
    "for location moves per company.",
    "author": "NuoBiT Solutions SL",
    "category": "Stock",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "stock_move_location",
    ],
    "data": [
        "views/stock_picking_type_views.xml",
    ],
}
