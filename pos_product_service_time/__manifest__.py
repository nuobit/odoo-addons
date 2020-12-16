# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'POS product service time',
    'version': '12.0.1.0.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Point of Sale',
    'website': 'https://github.com/nuobit',
    'summary': "Add the service time on POS order line.",
    'depends': [
        'point_of_sale',
        'product_service_time',
    ],
    'data': [
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
}
