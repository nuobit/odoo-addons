# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingETIMClassFeature(models.Model):
    _name = 'lighting.etim.class.feature'
    _order = 'sequence'

    sequence = fields.Integer("Order", required=True, default=1)

    change_code = fields.Char("Change code", required=True)

    feature_id = fields.Many2one(comodel_name='lighting.etim.feature', ondelete='restrict', string='Feature')
    unit_id = fields.Many2one(comodel_name='lighting.etim.unit', ondelete='restrict', string='Unit')

    value_ids = fields.One2many(comodel_name='lighting.etim.class.feature.value',
                                inverse_name='feature_id', string='Values')

    class_id = fields.Many2one(comodel_name='lighting.etim.class', ondelete='cascade', string='Class')


class LightingETIMClassFeatureValue(models.Model):
    _name = 'lighting.etim.class.feature.value'
    _order = 'sequence'

    sequence = fields.Integer("Order", required=True, default=1)

    change_code = fields.Char("Change code", required=True)

    value_id = fields.Many2one(comodel_name='lighting.etim.value', ondelete='restrict', string='Value')

    feature_id = fields.Many2one(comodel_name='lighting.etim.class.feature', ondelete='cascade', string='Feature')
