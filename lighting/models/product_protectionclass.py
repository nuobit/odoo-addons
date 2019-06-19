# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _, exceptions


class LightingProductProtectionClass(models.Model):
    _name = 'lighting.product.protectionclass'
    _order = 'name'

    name = fields.Char(string='Class', required=True, translate=True)

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count([('protection_class_id', '=', record.id)])

    _sql_constraints = [('name_uniq', 'unique (name)', 'The protection class must be unique!'),
                        ]
