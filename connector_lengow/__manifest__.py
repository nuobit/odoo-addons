# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Connector Lengow",
    'description': "Connector Lengow",
    'version': '11.0.0.1.17',
    'author': 'NuoBiT Solutions, S.L.',
    'license': 'AGPL-3',
    'category': 'Connector',
    'website': 'https://github.com/nuobit',
    'external_dependencies': {
        'python': [
            'requests',
        ],
    },
    'depends': [
        'connector_common',
        'sale_management',
    ],
    'data': [
        'security/connector_lengow.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/lengow_backend_view.xml',
        'views/sale_order_view.xml',
        'views/partner_view.xml',
        'views/product_product_view.xml',
        'views/connector_lengow_menu.xml',

    ],
    'installable': True,
}
