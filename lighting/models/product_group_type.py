# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductGroupType(models.Model):
    _name = 'lighting.product.group.type'
    _order = 'name'

    code = fields.Char(string='Code', required=True)

    name = fields.Char(string='Name', required=True)

    group_count = fields.Integer(compute='_compute_group_count', string='Group(s)')

    def _compute_group_count(self):
        for record in self:
            record.group_count = self.env['lighting.product.group'].search_count([('type_ids', '=', record.id)])

    @api.multi
    def unlink(self):
        records = self.env['lighting.product'].search([('type_ids', 'in', self.ids)])
        if records:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super().unlink()
