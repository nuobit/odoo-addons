# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock Barcodes Option New Scan",
    "summary": "Enable the new scan picking button in the barcode when the barcode "
    "option group of the new picking is informed",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        "stock_barcodes",
    ],
    "data": [
        "views/stock_picking_views.xml",
    ],
}
