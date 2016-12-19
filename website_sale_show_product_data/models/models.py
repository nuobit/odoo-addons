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

from openerp import api, models, fields, SUPERUSER_ID
from openerp.api import Environment


class ProductPrcelist(models.Model):
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

