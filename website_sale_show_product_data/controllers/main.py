# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import odoo.addons.website_sale.controllers.main as main


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
