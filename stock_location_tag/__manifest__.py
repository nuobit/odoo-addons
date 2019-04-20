# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Stock location tag",
    'summary': "This module adds tags on location",
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'category': 'Warehouse',
    'version': '11.0.0.1.0',
    'license': 'AGPL-3',
    'website': 'https://github.com/nuobit',
    'depends': [
        'stock',
    ],
    'data': [
        'security/stock_location_tag_security.xml',
        'security/ir.model.access.csv',
        'views/stock_location_views.xml',
        'views/stock_location_tag_views.xml',
    ],
    'installable': True,
}
