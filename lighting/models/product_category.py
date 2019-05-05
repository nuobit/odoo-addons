# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _


class LightingProductCategory(models.Model):
    _name = 'lighting.product.category'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    is_accessory = fields.Boolean(string="Is accessory")

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count([('category_id', '=', record.id)])

    _sql_constraints = [('name_uniq', 'unique (name)', 'The type must be unique!'),
                        ]
