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

from openerp import models, fields, api, _

class dt_product_template(models.Model):
    _inherit = "product.template"

    public_categ_sequence = fields.Integer(compute='_compute_public_categ_sequence', store=True)
    public_default_code = fields.Char(compute='_compute_public_default_code', store=True)

    @api.depends('public_categ_ids.sequence')
    def _compute_public_categ_sequence(self):
        for record in self:
            if record.public_categ_ids:
                record.public_categ_sequence = record.public_categ_ids[0].sequence

    @api.depends('product_variant_ids.default_code')
    def _compute_public_default_code(self):
        for record in self:
            if record.product_variant_ids:
                record.public_default_code = record.product_variant_ids[0].default_code


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    nondelivery_products_amount = fields.Float(compute='_compute_nondelivery_products_amount')

    @api.depends('website_order_line')
    def _compute_nondelivery_products_amount(self):
        self.nondelivery_products_amount = sum([x.price_subtotal for x in self.website_order_line])