# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import http
from odoo.http import request

import odoo.addons.website_sale.controllers.main as main


class WebsiteSale(main.WebsiteSale):
    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        category_ant = request.session.get('category_ant', None)
        request.session['category_ant'] = category.id if category is not None else None
        if search:
            if category:
                if category_ant and category_ant == category.id: # s'ha premut la lupa estant en una categoria
                    return request.redirect('/shop?search=%s' % search)
                else:
                    return request.redirect(request.httprequest.base_url)

        response = super(WebsiteSale, self).shop(page=page, category=category, search=search, ppg=ppg, **post)

        return response
