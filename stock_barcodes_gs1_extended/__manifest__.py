# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock Barcodes GS1 Extended",
    "summary": "This module extends barcode reader interface to allow to "
               "read more GS1 barcodes.",
    "version": "11.0.1.0.3",
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://github.com/nuobit',
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        'stock_barcodes_gs1',
    ],
    "data": [
        'wizard/stock_barcodes_read_picking_views.xml',
    ],
    'installable': True,
    'development_status': 'Beta',
    'maintainers': ['eantones'],
    'auto_install': True,
}
