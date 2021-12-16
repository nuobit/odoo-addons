# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Sale order Service',
    'summary': 'This module adds Service specific data to sale orders',
    'version': '11.0.0.3.0',
    'category': 'Sales',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://www.nuobit.com',
    'license': 'AGPL-3',
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
