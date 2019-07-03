# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _


class LightingProductCategory(models.Model):
    _name = 'lighting.product.category'
    _order = 'sequence'

    @api.model
    def _get_domain(self):
        model_id = self.env.ref('lighting.model_lighting_product').id
        return [('model_id', '=', model_id)]

    code = fields.Char(string='Code', size=3, required=True)

    name = fields.Char(required=True, translate=True)

    description_text = fields.Char(string='Description text', help='Text to show on a generated product description',
                                   translate=True)

    is_accessory = fields.Boolean(string="Is accessory")

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")

    attribute_ids = fields.Many2many(comodel_name='ir.model.fields',
                                     relation='lighting_product_category_field_attribute_rel',
                                     column1='category_id', column2='field_id',
                                     domain=_get_domain,
                                     string='Attributes')

    field_ids = fields.Many2many(comodel_name='ir.model.fields',
                                 relation='lighting_product_category_field_field_rel',
                                 column1='category_id', column2='field_id',
                                 domain=_get_domain,
                                 string='Fields')

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
                        ('code_uniq', 'unique (code)', 'The code must be unique!')
                        ]
