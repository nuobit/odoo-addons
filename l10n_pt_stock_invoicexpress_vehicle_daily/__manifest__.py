# Copyright 2025 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Portugal InvoiceXpress Vehicle Daily Integration",
    "summary": "Bridge module integrating InvoiceXpress transport "
    "documents with vehicle daily stock tracking for Portuguese Tax Authorities",
    "version": "18.0.1.0.0",
    "category": "Warehouse",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_pt_stock_invoicexpress",
        "l10n_pt_stock_vehicle_daily",
    ],
    "data": [
        "views/stock_picking_views.xml",
    ],
    "auto_install": True,
}
