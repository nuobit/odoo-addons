# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Connector Veloconnect",
    'description': "Connector Veloconnect",
    'version': '11.0.0.1.0',
    'author': 'NuoBiT Solutions, S.L., Kilian Niubo',
    'license': 'AGPL-3',
    'category': 'Connector',
    'website': 'https://github.com/nuobit',
    'external_dependencies': {
        'python': [
            'requests',
            'pyveloedi',
        ],
    },
    'depends': [
        'connector_common',
    ],
    'data': [
        'security/connector_veloconnect.xml',
        'security/ir.model.access.csv',
        # 'data/ir_cron.xml',
        'views/veloconnect_backend_view.xml',
        # 'views/sale_order_view.xml',
        # 'views/partner_view.xml',
        'views/product_template_view.xml',
        'views/connector_veloconnect_menu.xml',

    ],
    'installable': True,
}
