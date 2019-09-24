# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError


class LightingProduct(models.Model):
    _inherit = 'lighting.product'

    review_ids = fields.One2many(comodel_name='lighting.product.review',
                                 inverse_name='product_id',
                                 string='Reviews')
