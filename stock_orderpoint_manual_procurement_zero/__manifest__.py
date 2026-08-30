# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock Orderpoint Manual Procurement Zero",
    "summary": "Extends the module 'stock_orderpoint_manual_procurement' allowing "
    "users to remove procure recommendations with 0 quantity.",
    "author": "NuoBiT Solutions SL",
    "category": "Warehouse Management",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "stock_orderpoint_manual_procurement",
    ],
    "data": [
        "wizards/make_procurement_orderpoint_view.xml",
    ],
}
