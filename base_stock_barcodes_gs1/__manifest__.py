# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Base Stock Barcodes GS1",
    "summary": "Base module for stock barcodes using GS1 nomenclature",
    "version": "17.0.1.0.0",
    "category": "Extra Tools",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": ["stock", "barcodes_gs1_nomenclature"],
    "data": [
        "views/stock_picking_type_views.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["eantones"],
}
