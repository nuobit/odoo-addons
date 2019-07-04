# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductColorTemperature(models.Model):
    _name = 'lighting.product.color.temperature'
    _rec_name = 'value'
    _order = 'value'

    value = fields.Integer(string='Value', required=True)

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count(
                [('source_ids.line_ids.color_temperature_id', '=', record.id)])

    _sql_constraints = [('name_uniq', 'unique (value)', 'The color temperature must be unique!'),
                        ]

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%iK' % rec.value))
        return res
