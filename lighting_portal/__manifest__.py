# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting Portal",
    'description': "Lighting Portal",
    'version': '11.0.0.2.3',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': ['lighting'],
    'data': [
        'security/portal_security.xml',
        'security/ir.model.access.csv',
        'views/portal_views.xml',
        ],
    'installable': True,
}
