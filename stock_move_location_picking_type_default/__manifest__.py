# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Move Stock Location Picking Type Default",
    "summary": "This module allows defining a default picking type "
    "for location moves per company.",
    "author": "NuoBiT Solutions, S.L.",
    "category": "Stock",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "stock_move_location",
    ],
    "data": [
        "views/stock_picking_type_views.xml",
    ],
}
