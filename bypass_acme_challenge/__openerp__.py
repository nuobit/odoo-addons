# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name': 'Bypass Acme challenge',
    'description': """
        Allow Acme challenges like Let's Encrypt ones pass through Odoo server

        Usage: Add system parameter acme.challenge.webroot.folder with the local "webroot" mapped folder
    """,
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'version': '0.1.1',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'installable': True,
    'auto_install': True,
    'depends': [
        'base',
    ],
    'data': [

    ],
    'bootstrap': True,
}
