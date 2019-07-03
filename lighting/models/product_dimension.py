# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductDimension(models.Model):
    _name = 'lighting.product.dimension'
    _rec_name = 'type_id'
    _order = 'sequence'

    type_id = fields.Many2one(comodel_name='lighting.dimension.type', ondelete='restrict', string='Dimension',
                              required=True)
    value = fields.Float(string='Value', required=True)
    sequence = fields.Integer(required=True, default=1,
                              help="The sequence field is used to define order in which the dimension lines are sorted")

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')


class LightingProductRecessDimension(models.Model):
    _name = 'lighting.product.recessdimension'
    _rec_name = 'type_id'
    _order = 'sequence'

    type_id = fields.Many2one(comodel_name='lighting.dimension.type', ondelete='restrict', string='Dimension',
                              required=True)
    value = fields.Float(string='Value', required=True)
    sequence = fields.Integer(required=True, default=1,
                              help="The sequence field is used to define order in which the recess dimension lines are sorted")

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')
