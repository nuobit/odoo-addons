# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock picking delivery note",
    "summary": """Stock picking delivery note""",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Warehouse",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "stock",
        "sale_line_partner_description",
    ],
    "data": [
        "report/report.xml",
        "views/report_stock_picking_report_delivery_note.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "stock_picking_report_delivery_note/static/src/scss/stock_picking_report_delivery_note.scss"
        ],
    },
}
