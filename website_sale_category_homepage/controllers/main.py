# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import odoo.addons.website.controllers.main as main
from odoo import http
from odoo.http import request
from odoo.addons.website.models.website import slug

class Website(main.Website):
    @http.route()
    def index(self, **kw):
        category = request.env['product.public.category'].search([('is_homepage', '=', True)])
        if not category:
            return super(Website, self).index(**kw)
        category = category[0]

        page = 'homepage'
        main_menu = request.website.menu_id or request.env.ref('website.main_menu', raise_if_not_found=False)
        if main_menu:
            first_menu0 = main_menu.child_id and main_menu.child_id[0]

            first_menu = request.env.ref('website_sale.menu_shop', raise_if_not_found=False) or first_menu0
            if first_menu:
                if first_menu.url and (
                not (first_menu.url.startswith(('/page/', '/?', '/#')) or (first_menu.url == '/'))):
                    return request.redirect('%s/category/%s' % (first_menu.url, slug(category)))
                if first_menu.url and first_menu.url.startswith('/page/'):
                    return request.env['ir.http'].reroute(first_menu.url)

        return self.page(page)