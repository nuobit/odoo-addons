# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "GS1 Barcodes label Purchase",
    "summary": "Print the receipt labels of goods bought in a unit "
    "whose quantity is known on receipt",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "category": "Tools",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "barcodes_gs1_label",
        "purchase_stock",
    ],
    "data": [
        "views/uom_uom_views.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["eantones"],
}
