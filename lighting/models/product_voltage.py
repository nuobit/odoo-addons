# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductVoltage(models.Model):
    _name = 'lighting.product.voltage'
    _order = 'name'

    name = fields.Char(compute='_compute_name', string='Voltage', required=True)

    @api.depends('voltage1', 'voltage2', 'voltage2_check', 'current_type')
    def _compute_name(self):
        for record in self:
            voltage_l = []
            if record.voltage1 != 0:
                voltage_l.append('%i' % record.voltage1)

            if record.voltage2_check and record.voltage2 != 0:
                voltage_l.append('-%i' % record.voltage2)

            if voltage_l:
                voltage_l.append('V')

            if record.current_type:
                voltage_l.append(' %s' % record.current_type)

            if voltage_l:
                record.name = ''.join(voltage_l)

    voltage1 = fields.Integer(string="Voltage 1 (V)", required=True)
    voltage2_check = fields.Boolean(string="Voltage 2 check")
    voltage2 = fields.Integer(string="Voltage 2 (V)", required=False, default=None)

    @api.onchange('voltage2_check')
    def _onchange_voltage2_check(self):
        if not self.voltage2_check:
            self.voltage2 = False

    @api.constrains('voltage1', 'voltage2', 'voltage2_check')
    def _check_voltages(self):
        self.ensure_one()
        if self.voltage1 == 0:
            raise ValidationError("Voltage 1 cannot be 0")

        if self.voltage2_check and self.voltage2 == 0:
            raise ValidationError("Voltage 2 cannot be 0")

    current_type = fields.Selection(selection=[('AC', 'Alternating'), ('DC', 'Direct')], string="Current type",
                                    required=True)

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count(
                ['|',
                 ('input_voltage_id', '=', record.id),
                 ('output_voltage_id', '=', record.id)])

    _sql_constraints = [('voltage_uniq', 'unique (voltage1, voltage2, voltage2_check, current_type)',
                         'It already exists another voltage with the same parameters'),
                        ]
