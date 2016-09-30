# -*- coding: utf-8 -*-

{
    'name': 'Credit Payment Acquirer',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: Crèdit Implementation',
    'version': '8.0.0.1.0',
    'description': """Allow paying after delivery according to customer payment term""",
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'depends': ['payment'],
    'data': [
        'views/credit.xml',
        'data/credit.xml',
    ],
    'installable': True,
    'auto_install': True,
}
