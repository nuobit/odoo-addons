# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import odoo.addons.website_sale.controllers.main as main
from odoo import http
from odoo.http import request


class WebsiteSale(main.WebsiteSale):
    def _get_search_domain(self, search, category, attrib_values):

        domain = super(WebsiteSale, self)._get_search_domain(search, category, attrib_values)

        domain9 = []
        e0 = None
        for e in domain:
            if e0 == '|' and isinstance(e, tuple):
                field_name, operator, value = e
                if field_name == 'name':
                    domain9 += ['|', e, ('barcode', operator, value)]
            else:
                domain9.append(e)

            e0 = e

        return domain9

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        res = super(WebsiteSale, self).shop(page=page, category=category, search=search, ppg=ppg, **post)

        values = res.qcontext

        ### pricelists
        product_prices = {}

        if 'product' in values:
            pricelist_data = request.env['product.pricelist.item'].search(
                [('pricelist_id.show_on_website', '=', True), ('product_tmpl_id.id', 'in', values['products'].ids)],
                order='product_tmpl_id, min_quantity'
            )

            if pricelist_data:
                for pricelist_item in pricelist_data:
                    product_id = pricelist_item.product_tmpl_id.id
                    if product_id not in product_prices:
                        product_prices[product_id]=[]
                    product_prices[product_id].append({'fixed_price': pricelist_item.fixed_price,
                                           'min_quantity': pricelist_item.min_quantity},
                                        )

        values['website_prices'] = product_prices

        ### offers
        product_offers = {}

        if 'product' in values:
            priceoffer_pricelist = request.env['product.pricelist.item'].search([('pricelist_id.show_on_website', '=', True),
                                                                                 ('applied_on', '=', '3_global'),
                                                                                 ('compute_price', '=', 'formula'),
                                                                                 ('base', '=', 'pricelist')])
            if priceoffer_pricelist:
                offer_pricelist_id = priceoffer_pricelist.base_pricelist_id.id
                priceoffer_data = request.env['product.pricelist.item'].search(
                    [('pricelist_id', '=', offer_pricelist_id), ('product_tmpl_id.id', 'in', values['products'].ids)],
                    order='product_tmpl_id, min_quantity'
                )
                if priceoffer_data:
                    for pricelist_item in priceoffer_data:
                        product_id = pricelist_item.product_tmpl_id.id
                        if product_id not in product_offers:
                            product_offers[product_id] = []
                        product_offers[product_id].append({'fixed_price': pricelist_item.fixed_price,
                                                           'min_quantity': pricelist_item.min_quantity},
                                                          )
        values['website_offers'] = product_offers

        return request.render("website_sale.products", values)
