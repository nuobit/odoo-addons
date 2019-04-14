# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Account journal balance',
    'description': 'This module adds a journal filtered balance in account dashboard',
    'version': '10.0.0.1.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://www.nuobit.com',
    'depends': [
        'account'
    ],
    'data': [
        'views/account_journal_dashboard_view.xml',
    ],
    'installable': True,
}
