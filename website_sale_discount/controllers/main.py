# -*- coding: utf-8 -*-
#/#############################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2015 NuoBiT Solutions, S.L. (<http://www.nuobit.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#/#############################################################################

import openerp.addons.website_sale.controllers.main as main

from openerp import http
from openerp.http import request


class website_sale(main.website_sale):
    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_json(self, product_id, line_id, add_qty=None, set_qty=None, display=True):

        value = super(website_sale, self).cart_update_json(product_id, line_id, add_qty, set_qty, display)

        order_obj = request.website.sale_get_order()
        if order_obj:
            order_line_obj = order_obj.order_line.search([('id', '=', line_id)])

            lang_code = request.context['lang']
            lang_obj = request.env['res.lang'].search([('code', '=', lang_code)])

            value['price_unit'] = lang_obj.format('%.2f', order_line_obj.price_unit, grouping=True, monetary=True)
            value['discount'] = lang_obj.format('%.2f', order_line_obj.discount, grouping=True, monetary=False)
            value['price_subtotal'] = lang_obj.format('%.2f', order_line_obj.price_subtotal, grouping=True, monetary=True)

        return value


    """
    @http.route(['/shop/get_unit_price_discount'], type='json', auth="public", methods=['POST'], website=True)
    def get_unit_price_discount(self, product_ids, add_qty, line_id, **kw):
        products = request.env['product.product'].browse(product_ids)
        partner = request.env['res.users'].browse(request.uid).partner_id
        pricelist_id = request.session.get('sale_order_code_pricelist_id') or partner.property_product_pricelist.id

        pricelist_obj = request.env['product.pricelist'].browse(pricelist_id)
        prices = pricelist_obj.price_rule_get_multi([(product, add_qty, partner) for product in products])

        res = {}
        for product in products:
            price_net, rule_id = prices[product.id][pricelist_id]
            rule_obj = request.env['product.pricelist.item'].browse(rule_id)
            if rule_obj.price_discount == -1.0 and rule_obj.price_surcharge!=0.0: # es un net
                price = rule_obj.price_surcharge
                discount = 0.0
            else:
                price = product.list_price
                if price>0:
                    discount = (1.0 - price_net / price) * 100.0
                else:
                    discount = 0.0

            res[product.id]=(price, discount, price_net * add_qty)

        return res
    """
