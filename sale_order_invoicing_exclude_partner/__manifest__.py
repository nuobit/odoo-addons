# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Sale order invoicing exclude partner',
    'summary': "Exclude partner from being invoiced.",
    'version': '11.0.1.0.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://github.com/nuobit',
    'depends': [
        'sale',
    ],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'development_status': 'Beta',
    'maintainers': ['eantones'],
}
