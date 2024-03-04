# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock Barcodes Unique Field",
    "summary": "This module extends the barcode options in inventory,"
    " allowing items to be marked as unique and specifying the copy "
    "of these characteristics to the picking header",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions",
    "website": "https://github.com/nuobit/odoo-addons",
    "category": "Stock",
    "depends": ["stock_barcodes"],
    "license": "AGPL-3",
    "data": [
        "views/stock_barcodes_option_view.xml",
    ],
}
