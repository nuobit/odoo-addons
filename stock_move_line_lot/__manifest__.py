# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Stock move line lot",
    'description': "This module adds field lot to stock move line tree view",
    'version': '12.0.1.0.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://github.com/nuobit',
    'depends': [
        'stock',
    ],
    'data': [
        'views/stock_move_line_views.xml',
    ],
    'installable': True,
}
