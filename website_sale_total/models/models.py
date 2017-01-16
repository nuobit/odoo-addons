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

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    nondelivery_products_amount = fields.Float(compute='_compute_nondelivery_products_amount')

    @api.depends('website_order_line')
    def _compute_nondelivery_products_amount(self):
        self.nondelivery_products_amount = sum([x.price_subtotal for x in self.website_order_line])



