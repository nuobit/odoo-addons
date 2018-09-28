# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields
from odoo.tools.translate import _


class ProductProduct(models.Model):
    _inherit = "product.product"

    company_id = fields.Many2one(
        'res.company', 'Company',
        related='product_tmpl_id.company_id', store=True)

    _sql_constraints = [
        ('default_code_uniq', 'unique(company_id, default_code)',
         _("A internal reference can only be assigned to one product per company!")),
    ]