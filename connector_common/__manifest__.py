# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Odoo connector to share common behaviour across several connectors.",
    'version': '11.0.0.3.1',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Connector',
    'website': 'https://www.nuobit.com',
    'depends': [
        'connector',
        'sale',
    ],
    'data': [
        'views/product_product_view.xml',
        'views/product_category_view.xml',
        'views/country_state_view.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': True,
}
