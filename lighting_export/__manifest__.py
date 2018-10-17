# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting Export",
    'description': "Lighting export data",
    'version': '11.0.0.8.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': ['lighting', 'report_xlsx'],
    'data': [
        'views/export_template_views.xml',
        'wizard/export_views.xml',
        'report/export_product_xlsx.xml',
        ],
    'installable': True,
}
