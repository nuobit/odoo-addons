# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale

_logger = logging.getLogger(__name__)


class WebsiteSale(website_sale):
    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', **post):
        resp = super(WebsiteSale, self).shop(page, category, search, **post)

        values = resp.qcontext

        category = values['category']
        if category:
            if not category.get_access():
                values['category'] = None

        values['categories'] = values['categories'].filtered(lambda x: x.get_access())

        return request.website.render("website_sale.products", values)

    def _get_search_domain(self, search, category, attrib_values):
        domain = super(WebsiteSale, self)._get_search_domain(search, category, attrib_values)

        for pubcat_obj in request.env['product.public.category'].search([]):
            if not pubcat_obj.get_access():
                domain += ['!', ('public_categ_ids', 'child_of', pubcat_obj.id)]

        return domain

