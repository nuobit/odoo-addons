# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductSourceLineColorTemperatureFlux(models.Model):
    _name = 'lighting.product.source.line.color.temperature.flux'
    _order = 'color_temperature_value'

    color_temperature_id = fields.Many2one(string='Color temperature (K)',
                                           comodel_name='lighting.product.color.temperature',
                                           required=True,
                                           ondelete='restrict')
    color_temperature_value = fields.Integer(related='color_temperature_id.value', store=True)

    flux_id = fields.Many2one(string='Luminous flux (lm)',
                              comodel_name='lighting.product.flux',
                              required=True,
                              ondelete='restrict')

    source_line_id = fields.Many2one(comodel_name='lighting.product.source.line',
                                     required=True,
                                     ondelete='cascade')

    _sql_constraints = [('k_uniq', 'unique (source_line_id, color_temperature_id)',
                         'The color temperature must be unique per source line'),
                        ('lm_uniq', 'unique (source_line_id, flux_id)',
                         'The luminous flux must be unique per source line'),
                        ]
