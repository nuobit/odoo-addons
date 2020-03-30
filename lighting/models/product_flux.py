# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductFlux(models.Model):
    _name = 'lighting.product.flux'
    _rec_name = 'value'
    _order = 'value'

    value = fields.Integer(string='Value', required=True)

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count(
                [('source_ids.line_ids.color_temperature_flux_ids.flux_id', 'in', [record.id])])

    _sql_constraints = [('name_uniq', 'unique (value)', 'The flux must be unique!'),
                        ]

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%ilm' % rec.value))
        return res

    @api.multi
    def unlink(self):
        records = self.env['lighting.product.source.line'].search([
            ('color_temperature_flux_ids.flux_id', 'in', self.ids)])
        if records:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super().unlink()
