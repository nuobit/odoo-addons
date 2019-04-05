# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting JSON Export",
    'description': "Lighting export data JSON",
    'version': '11.0.0.14.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://github.com/nuobit',
    'depends': ['lighting_export', 'report_json'],
    'data': [
        'report/export_product_json_reports.xml',
        'views/export_template_views.xml',
        'wizard/export_views.xml',
    ],
    'installable': True,
}
