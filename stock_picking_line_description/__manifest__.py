# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Stock picking line description",
    'summary': "Adds description on picking lines.",
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'category': 'Warehouse',
    'version': '11.0.0.2.0',
    'license': 'AGPL-3',
    'website': 'https://github.com/nuobit',
    'depends': [
        'stock',
    ],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
}
