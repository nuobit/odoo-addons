# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductSourceType(models.Model):
    _name = 'lighting.product.source.type'
    _rec_name = 'code'
    _order = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', help='Source description', translate=True)

    is_led = fields.Boolean(string='Is LED?')
    is_integrated = fields.Boolean(string='Is integrated?')

    description_text = fields.Char(string='Description text', help='Text to show on a generated product description',
                                   translate=True)

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count([('source_ids.line_ids.type_id', '=', record.id)])

    _sql_constraints = [('name_uniq', 'unique (name)', 'The source type description must be unique!'),
                        ('code_uniq', 'unique (code)', 'The source type code must be unique!'),
                        ]
