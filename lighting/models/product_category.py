# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _


class LightingProductCategory(models.Model):
    _name = 'lighting.product.category'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    is_accessory = fields.Boolean(string="Is accessory")

    description_text = fields.Char(string='Description text', help='Text to show on a generated product description',
                                   translate=True)

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count([('category_id', '=', record.id)])

    attachment_ids = fields.One2many(comodel_name='lighting.product.category.attachment',
                                     inverse_name='category_id', string='Attachments', copy=True,
                                     track_visibility='onchange')
    attachment_count = fields.Integer(compute='_compute_attachment_count', string='Attachment(s)')

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = self.env['lighting.product.category.attachment'] \
                .search_count([('category_id', '=', record.id)])

    _sql_constraints = [('name_uniq', 'unique (name)', 'The type must be unique!'),
                        ]
