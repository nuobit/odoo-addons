# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting Portal",
    'description': "Lighting Portal",
    'version': '11.0.0.6.1',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': [
        'lighting',
        'report_xml',
    ],
    'data': [
        'security/portal_security.xml',
        'security/ir.model.access.csv',
        'report/report.xml',
        'views/portal_views.xml',
        'views/report_product_xml.xml',
    ],
    'installable': True,
}
