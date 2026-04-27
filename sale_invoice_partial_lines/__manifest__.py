# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Invoice Partial Lines",
    "summary": "Mark sale order lines and invoice only the marked ones",
    "author": "NuoBiT Solutions SL",
    "category": "Sales",
    "version": "16.0.1.2.1",
    "license": "AGPL-3",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "sale",
    ],
    "data": [
        "views/sale_order_views.xml",
        "wizards/sale_advance_payment_inv_views.xml",
    ],
}
