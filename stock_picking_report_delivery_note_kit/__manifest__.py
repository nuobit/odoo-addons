# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


{
    "name": "Stock picking delivery note kit",
    "summary": "Stock picking delivery note kit",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Warehouse",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "stock_whole_kit_constraint",
        "stock_picking_report_delivery_note",
    ],
    "data": [
        "views/report_stock_picking_report_delivery_note.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "stock_picking_report_delivery_note_kit/static/src/scss/stock_picking_report_delivery_note.scss"
        ],
    },
}
