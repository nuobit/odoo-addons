# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = "product.product"

    company_id = fields.Many2one(
        'res.company', 'Company',
        related='product_tmpl_id.company_id', store=True)
