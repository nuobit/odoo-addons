# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock Barcodes Option New Scan",
    "summary": "Enable the new scan picking button in the barcode when the barcode "
    "option group of the new picking is informed",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        "stock_barcodes",
    ],
    "data": [
        "views/stock_picking_views.xml",
    ],
}
