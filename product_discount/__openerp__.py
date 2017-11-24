##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
    'name': 'Product discount',
    'version': '8.0.0.1.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'category': 'Sales Management',
    'website': 'https://www.nuobit.com',
    'description': """
This module lets you calculate discounts on Sale Order lines, Purchase Order lines based on the partner's pricelist.
====================================================================================================================

To this end, a new field 'Discount' is added to the purchase order line, the sale order line and invoice line already have this field in the standard.

This module is not compatible with product_visible_discount and purchase_discount

**Example:**
    For the product PC1 and the partner "Asustek": if listprice=450, and the price
    calculated using Asustek's pricelist is 225. If this module is installed, we
    will have on the sale order line: Unit price=450, Discount=50,00, Net price=225.
    If the modeule is not installed, we will have on Sale Order and Invoice lines:
    Unit price=225, Discount=0,00, Net price=225.
    """,
    'depends': ["sale", "purchase", "pricelist_extended"],
    'demo': [],
    'data': ['product_discount_view.xml',
             'report_purchaseorder.xml'],
    'auto_install': False,
    'installable': True,
}

