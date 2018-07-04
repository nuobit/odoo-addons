# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting Portal Product report",
    'description': "Lighting Portal Product report datasheet",
    'version': '11.0.0.1.4',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': ['lighting_portal'],
    'data': [
        'report/portal_product_report.xml',
        'report/portal_product_report_templates.xml',
        'views/portal_views.xml',
        ],
    'installable': True,
}
