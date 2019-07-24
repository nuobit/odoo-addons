# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductLocation(models.Model):
    _name = 'lighting.product.location'
    _order = 'name'

    name = fields.Char(string='Name', required=True, translate=True)

    code = fields.Char(string='Code', size=5, required=True)

    description_text = fields.Char(string='Description text', help='Text to show', translate=True)

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count([('location_ids', '=', record.id)])

    color = fields.Integer(string='Color Index')

    _sql_constraints = [('name_uniq', 'unique (name)', 'The location must be unique!'),
                        ]

    @api.multi
    def unlink(self):
        records = self.env['lighting.product'].search([('location_ids', 'in', self.ids)])
        if records:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super().unlink()
