# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Portugal InvoiceXpress Vehicle Daily Integration",
    "summary": "Bridge module integrating InvoiceXpress transport "
    "documents with vehicle daily stock tracking for Portuguese Tax Authorities",
    "version": "14.0.1.0.0",
    "category": "Warehouse",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
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
