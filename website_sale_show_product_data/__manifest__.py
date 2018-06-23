# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Show product data in website sale",
    'description': "Show product data in website sale: "
                   "internal reference (default code), providers, "
                   "helper text, print button, barcode ",
    'version': '10.0.0.3.3',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': ['website_sale'],
    'data': [
        'views/website_sale_show_product_data_templates.xml',
        'views/inherit_views.xml',
        ],
    'installable': True,
}
