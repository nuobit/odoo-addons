# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ProductBuyerInfo(models.Model):
    _name = 'product.buyerinfo'

    partner_id = fields.Many2one(comodel_name='res.partner',
                                 domain=[('customer', '=', True)], ondelete='cascade',
                                 string='Customer', required=True)

    name = fields.Text(string='Description', required=True, translate=True)

    concatenate = fields.Boolean(string='Concatenate')

    product_id = fields.Many2one(comodel_name='product.product', required=True, ondelete='cascade')

    _sql_constraints = [
        ('buyerinfo_uniq', 'unique(product_id, partner_id)', "Already exists this same line!"),
    ]
