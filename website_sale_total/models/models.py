# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    nondelivery_products_amount = fields.Float(compute='_compute_nondelivery_products_amount')

    @api.depends('website_order_line')
    def _compute_nondelivery_products_amount(self):
        self.nondelivery_products_amount = sum([x.price_subtotal for x in self.website_order_line])



