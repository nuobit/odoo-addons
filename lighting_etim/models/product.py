# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProduct(models.Model):
    _inherit = 'lighting.product'

    class_id = fields.Many2one(comodel_name='lighting.etim.class', ondelete='restrict', string='Class')
    feature_ids = fields.One2many(comodel_name='lighting.etim.product.feature',
                                  inverse_name='product_id', string='Features', copy=True)
