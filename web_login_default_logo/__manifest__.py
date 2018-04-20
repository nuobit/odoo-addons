# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Web login default logo',
    'summary': 'This module force default Odoo logo at login login screen.',
    'version': '10.0.0.1.0',
    'category': 'Web',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://www.nuobit.com',
    'license': 'AGPL-3',
    'depends': [
        'web',
    ],
    'data': [
        'views/website_templates.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
}
