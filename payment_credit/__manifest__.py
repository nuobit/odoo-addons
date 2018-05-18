# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Credit Payment Acquirer',
    'summary': 'Payment Acquirer: Credit Implementation',
    'description': 'Credit Payment Acquirer',
    'version': '10.0.0.1.0',
    'category': 'Accounting',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://www.nuobit.com',
    'license': 'AGPL-3',
    'depends': ['payment'],
    'data': [
        'views/payment_credit_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
}

