# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import api, models, fields, SUPERUSER_ID
from openerp.api import Environment


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    show_on_website = fields.Boolean(string="Show on website", default=False)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    first_seller_image = fields.Char(string="First seller image", compute="_compute_first_seller_image")

    first_seller = fields.Many2one(string="First seller", comodel_name="res.partner", compute="_compute_first_seller")

    @api.depends('seller_ids')
    def _compute_first_seller_image(self):
        first_seller = self.sudo().seller_ids.sorted(lambda x: (x.sequence, x.id))[0].name

        self.first_seller_image = first_seller.image

    @api.depends('seller_ids')
    def _compute_first_seller(self):
        self.first_seller = self.sudo().seller_ids.sorted(lambda x: (x.sequence, x.id))[0].name

    def get_website_alternate_prices(self):
        res = {}
        ### pricelists
        product_prices = []

        pricelist_data = self.env['product.pricelist.item'].search(
            [('pricelist_id.show_on_website', '=', True), ('product_tmpl_id.id', '=', self.id)],
            order='product_tmpl_id, min_quantity'
        )

        if pricelist_data:
            for pricelist_item in pricelist_data:
                product_prices.append({'fixed_price': pricelist_item.fixed_price,
                                       'min_quantity': pricelist_item.min_quantity},
                                    )

        res['website_prices'] = product_prices

        ### offers
        product_offers = []

        priceoffer_pricelist = self.env['product.pricelist.item'].search([('pricelist_id.show_on_website', '=', True),
                                                                             ('applied_on', '=', '3_global'),
                                                                             ('compute_price', '=', 'formula'),
                                                                             ('base', '=', 'pricelist')])
        if priceoffer_pricelist:
            offer_pricelist_id = priceoffer_pricelist.base_pricelist_id.id
            priceoffer_data = self.env['product.pricelist.item'].search(
                [('pricelist_id', '=', offer_pricelist_id), ('product_tmpl_id.id', '=', self.id)],
                order='product_tmpl_id, min_quantity'
            )
            if priceoffer_data:
                for pricelist_item in priceoffer_data:
                    product_offers.append({'fixed_price': pricelist_item.fixed_price,
                                                       'min_quantity': pricelist_item.min_quantity},
                                          )
        res['website_offers'] = product_offers

        return res
