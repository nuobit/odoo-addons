# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting Export",
    'description': "Lighting export data",
    'version': '11.0.1.2.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://github.com/nuobit',
    'depends': ['lighting'],
    'data': [
        'security/export_security.xml',
        'security/ir.model.access.csv',
        'wizard/export_views.xml',
        'views/export_template_views.xml',
        ],
    'installable': True,
}
