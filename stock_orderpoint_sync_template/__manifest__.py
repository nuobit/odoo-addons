# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock orderpoint sync template",
    "summary": "Allows create reordering rules for multiple products and different "
    "parameters per product in one go and keep them synchronized with "
    "the base template",
    "author": "NuoBiT Solutions SL",
    "category": "Warehouse",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_warehouse_orderpoint_views.xml",
        "views/stock_warehouse_orderpoint_sync_template_views.xml",
        "security/orderpoint_sync_template_security.xml",
        "security/ir.model.access.csv",
    ],
}
