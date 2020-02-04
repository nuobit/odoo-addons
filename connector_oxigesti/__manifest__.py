# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Oxigesti-Odoo connector",
    'version': '11.0.0.7.9',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Connector',
    'website': 'https://www.nuobit.com',
    'depends': [
        'connector_common',
        'partner_review',
        'sale_line_partner_description',
        'stock',
    ],
    'external_dependencies': {
        'python': [
            'pymssql',
            'json',
            'hashlib',
        ],
    },
    'data': [
        'data/ir_cron.xml',
        'views/oxigesti_backend_view.xml',
        'views/partner_view.xml',
        'views/product_product_view.xml',
        'views/product_buyerinfo_view.xml',
        'views/product_pricelist_item_view.xml',
        'views/sale_order_view.xml',
        'views/connector_oxigesti_menu.xml',
        'security/connector_oxigesti.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
