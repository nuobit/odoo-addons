# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting vertical",
    'description': "Lighting vertical",
    'version': '11.0.0.9.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': [],
    'data': [
        'security/lighting_security.xml',
        'security/connector_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/connector_views.xml',
        'wizard/lighting_product_addattachment.xml',
        'wizard/connector_product_sync_views.xml',
        'data/lighting_data.xml',
        'data/lighting_data_etim.xml',
        'data/connector_data.xml',
        'report/connector_report.xml',
        'report/connector_report_templates.xml',
        ],
    'installable': True,
}
