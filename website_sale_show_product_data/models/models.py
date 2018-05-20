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

