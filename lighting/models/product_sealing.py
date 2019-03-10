# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductSealing(models.Model):
    _name = 'lighting.product.sealing'
    _order = 'name'

    name = fields.Char(string='Name', required=True)

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count([
                '|', ('sealing_id', '=', record.id), ('sealing2_id', '=', record.id)
            ])

    _sql_constraints = [('name_uniq', 'unique (name)', 'The sealing must be unique!'),
                        ]

    @api.multi
    def unlink(self):
        records = self.env['lighting.product'].search([
            '|', ('sealing_id', 'in', self.ids), ('sealing2_id', 'in', self.ids)
        ])
        if records:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super().unlink()
