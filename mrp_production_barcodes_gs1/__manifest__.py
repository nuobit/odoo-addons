# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "MRP Production Barcodes GS1",
    "summary": "Add products to manufacturing orders using scanned GS1 barcodes.",
    "version": "17.0.1.0.0",
    "category": "Extra Tools",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": ["mrp", "base_stock_barcodes_gs1"],
    "data": [
        "data/barcodes_gs1_rules.xml",
        "views/mrp_production_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mrp_production_barcodes_gs1/static/src/components/barcode_scanner_field/barcode_scanner_field.esm.js",
            "mrp_production_barcodes_gs1/static/src/components/barcode_scanner_field/barcode_scanner_field.xml",
        ],
    },
    "development_status": "Beta",
    "maintainers": ["deeniiz"],
}
