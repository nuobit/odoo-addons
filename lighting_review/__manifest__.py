# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting Review",
    'description': "Tools for reviewing data",
    'version': '11.0.0.1.2',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://github.com/nuobit',
    'depends': ['mail', 'lighting'],
    'data': [
        'security/review_security.xml',
        'security/ir.model.access.csv',
        'views/review_menuitems.xml',
        'views/review_package_views.xml',
        'views/product_views.xml',
        'views/product_review_views.xml',
    ],
    'installable': True,
}
