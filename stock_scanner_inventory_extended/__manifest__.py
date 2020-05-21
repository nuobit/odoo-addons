# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Stock Scanner Inventory Extended',
    'summary': 'This module extend the functionality of the stock_scanner_'
               'inventory module allowing to scan also barcodes of products '
               'and locations and improving the management of unexpected cases '
               'like multiple product and location matches.',
    'version': '11.0.1.0.0',
    'development_status': 'Beta',
    'category': 'Generic Modules/Inventory Control',
    'website': 'https://github.com/OCA/stock-logistics-barcode',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'maintainers': ['eantones'],
    'installable': True,
    'depends': [
        'stock_scanner',
    ],
    'data': [
        'data/Inventory_extended/Inventory_extended.scenario',
    ],
}
