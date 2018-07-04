# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    is_homepage = fields.Boolean(string="Is Homepage?")