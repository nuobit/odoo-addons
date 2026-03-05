# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Signature",
    "summary": "Configurable signature requirement per picking type",
    "author": "NuoBiT Solutions SL",
    "maintainers": ["eantones"],
    "category": "Warehouse",
    "development_status": "Alpha",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_picking_type_views.xml",
        "views/stock_picking_views.xml",
        "report/report_deliveryslip.xml",
        "report/report_stockpicking_operations.xml",
    ],
    "installable": True,
}
