# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting vertical",
    'description': "Lighting vertical",
    'version': '11.0.0.23.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': [],
    'data': [
        'security/lighting_security.xml',
        'security/ir.model.access.csv',
        'views/product_menuitems.xml',
        'views/product_catalog_views.xml',
        'views/product_family_views.xml',
        'views/product_type_views.xml',
        'views/product_application_views.xml',
        'views/product_finish_views.xml',
        'views/product_voltage_views.xml',
        'views/product_attachment_views.xml',
        'views/product_source_lampholder_views.xml',
        'views/product_source_type_views.xml',
        'views/views.xml',
        'wizard/lighting_product_addattachment.xml',
        'wizard/product_define_substitute_views.xml',
        'data/lighting_data.xml',
    ],
    'installable': True,
}
