# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _


class LightingProductGroup(models.Model):
    _name = 'lighting.product.group'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence,name'
    _description = 'Product group'

    name = fields.Char(required=True, track_visibility='onchange')

    sequence = fields.Integer(required=True, default=1,
                              help="The sequence field is used to define order",
                              track_visibility='onchange')

    attribute_ids = fields.Many2many(comodel_name='lighting.product.attribute',
                                     relation='lighting_product_group_attribute_rel',
                                     column1='group_id', column2='attribute_id',
                                     string='Attributes',
                                     required=True,
                                     track_visibility='onchange')
    product_ids = fields.One2many(comodel_name='lighting.product',
                                  inverse_name='product_group_id', string='Products')

    def _compute_attachment(self):
        for rec in self:
            pictures = rec.product_ids.mapped('attachment_ids') \
                .filtered(lambda x: x.type_id.code == 'F') \
                .sorted(lambda x: (x.product_id.sequence, x.sequence))
            if pictures:
                rec.picture_id = pictures[0]

    picture_id = fields.Many2one(comodel_name='lighting.attachment',
                                 compute='_compute_attachment')

    picture_datas = fields.Binary(related='picture_id.datas', string='Picture', readonly=True)
    picture_datas_fname = fields.Char(related='picture_id.datas_fname', readonly=True)

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for rec in self:
            rec.product_count = self.env['lighting.product'].search_count([('product_group_id', '=', rec.id)])

    _sql_constraints = [('name_uniq', 'unique (name)', 'The name must be unique!'),
                        ]
