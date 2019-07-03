# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductMaterial(models.Model):
    _name = 'lighting.product.material'
    _order = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', required=True, translate=True)

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count([
                '|', '|', '|', '|', ('body_material_ids', '=', record.id),
                ('diffusor_material_ids', '=', record.id), ('frame_material_ids', '=', record.id),
                ('reflector_material_ids', '=', record.id), ('blade_material_ids', '=', record.id)])

    _sql_constraints = [('name_uniq', 'unique (name)', 'The material name must be unique!'),
                        ('code_uniq', 'unique (code)', 'The material code must be unique!'),
                        ]

    @api.multi
    def unlink(self):
        fields = ['body_material_ids', 'diffusor_material_ids', 'frame_material_ids',
                  'reflector_material_ids', 'blade_material_ids']
        for f in fields:
            records = self.env['lighting.product'].search([(f, 'in', self.ids)])
            if records:
                raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(LightingProductMaterial, self).unlink()
