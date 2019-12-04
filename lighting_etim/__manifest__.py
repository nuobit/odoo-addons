# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting ETIM",
    'description': "Lighting ETIM",
    'version': '11.0.0.1.3',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': ['lighting'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_menuitems.xml',
        'views/product_views.xml',
        'views/etim_group_views.xml',
        'views/etim_class_views.xml',
        'views/etim_feature_views.xml',
        'views/etim_value_views.xml',
        'views/etim_unit_views.xml',
        'views/etim_class_feature_views.xml',
        'views/etim_product_feature_views.xml',
    ],
    'installable': True,
}
