# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductETIMFeature(models.Model):
    _name = 'lighting.etim.product.feature'

    feature_id = fields.Many2one(comodel_name='lighting.etim.feature', ondelete='restrict', string='Feature')

    @api.onchange('feature_id')
    def feature_id_change(self):
        self.unit_id = self.product_id.class_id.feature_ids.filtered(
            lambda x: x['feature_id'] == self.feature_id).unit_id
        feature_value_ids = self.product_id.class_id.feature_ids.filtered(
            lambda x: x['feature_id'] == self.feature_id).value_ids.mapped('value_id.id')

        return {'domain': {'unit_id': [('id', '=', self.unit_id.id)],
                           'a_value_id': [('id', 'in', feature_value_ids)]
                           },
                }

    feature_type = fields.Selection(related='feature_id.type', string="Type", readonly=True)

    unit_id = fields.Many2one(comodel_name='lighting.etim.unit', ondelete='restrict', string='Unit', readonly=True)
    has_unit = fields.Boolean(compute="_compute_has_unit")

    @api.depends('feature_id')
    def _compute_has_unit(self):
        for rec in self:
            unit_ids = rec.product_id.class_id.feature_ids.filtered(
                lambda x: x['feature_id'] == rec.feature_id).unit_id

            rec.has_unit = len(unit_ids) != 0

    a_value_id = fields.Many2one(comodel_name='lighting.etim.value', ondelete='restrict', string='Value')
    l_value = fields.Boolean('Value')
    n_value = fields.Float('Value')
    r1_value = fields.Float('Value 1')
    r2_value = fields.Float('Value 2')

    value = fields.Char(compute='_compute_value', string='Value', readonly=True)

    @api.depends('feature_id', 'a_value_id', 'l_value', 'n_value', 'r1_value', 'r2_value')
    def _compute_value(self):
        for rec in self:
            if rec.feature_id.type == 'A':
                rec.value = rec.a_value_id.display_name
            elif rec.feature_id.type == 'L':
                rec.value = 'True' if rec.l_value else 'False'
            elif rec.feature_id.type == 'N':
                rec.value = str(rec.n_value)
            elif rec.feature_id.type == 'R':
                range_str = []
                if rec.r1_value:
                    range_str.append(str(rec.r1_value))
                if rec.r2_value:
                    range_str.append(str(rec.r2_value))
                if range_str != []:
                    rec.value = ' - '.join(range_str)

    product_class_id = fields.Many2one(related='product_id.class_id', readonly=True)
    # @api.onchange('product_class_id')
    # def product_class_id_change(self):
    #     return {'domain': {'feature_id': [('id', 'in', self.product_id.class_id.feature_ids.mapped('feature_id.id'))]}}

    product_class_feature_ids = fields.One2many(comodel_name='lighting.etim.feature',
                                                compute="_product_class_feature_ids", readonly=True)

    @api.depends('product_class_id')
    def _product_class_feature_ids(self):
        for rec in self:
            rec.product_class_feature_ids = rec.product_id.class_id.feature_ids.mapped('feature_id')

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product', required=True)

    _sql_constraints = [
        ('feature_uniq', 'unique (feature_id, product_id)', 'Feature duplicated'),
    ]
