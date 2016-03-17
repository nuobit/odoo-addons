# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Product Relation',
    'version': '0.1',
    'category': 'Generic Modules',
    'description': """
This module adds relations between products:

- cross-selling
- up-selling

    """,
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://www.nuobit.com',
    'license': 'AGPL-3',
    'depends': ['product', 'sale'],
    'data': [
        #'security/ir.model.access.csv',
        'views/product_relation_view.xml',
        'views/product_relation_view_inherit.xml',
        'views/template_views.xml',
    ],
        'qweb': ['static/src/xml/*.xml'],
    'installable': True,
}
