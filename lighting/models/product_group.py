# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LightingProductGroup(models.Model):
    _name = 'lighting.product.group'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Product group'
    _parent_name = 'parent_id'
    _rec_name = 'complete_name'
    _order = 'sequence,name'

    name = fields.Char(required=True, track_visibility='onchange')

    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for rec in self:
            if rec.parent_id:
                rec.complete_name = '%s / %s' % (rec.parent_id.complete_name, rec.name)
            else:
                rec.complete_name = rec.name

    sequence = fields.Integer(required=True, default=1,
                              help="The sequence field is used to define order",
                              track_visibility='onchange')

    attribute_ids = fields.Many2many(comodel_name='lighting.product.attribute',
                                     relation='lighting_product_group_attribute_rel',
                                     column1='group_id', column2='attribute_id',
                                     string='Attributes',
                                     track_visibility='onchange')
    product_ids = fields.One2many(comodel_name='lighting.product',
                                  inverse_name='product_group_id', string='Products')

    parent_id = fields.Many2one(comodel_name='lighting.product.group', string='Parent',
                                index=True, ondelete='cascade')
    child_ids = fields.One2many(comodel_name='lighting.product.group', inverse_name='parent_id',
                                string='Child Groups')

    _sql_constraints = [('name_uniq', 'unique (name)', 'The name must be unique!'),
                        ]

    picture_id = fields.Many2one(comodel_name='lighting.attachment',
                                 compute='_compute_attachment')

    def _compute_attachment(self):
        for rec in self:
            pictures = rec.flat_product_ids.mapped('attachment_ids') \
                .filtered(lambda x: x.type_id.code == 'F') \
                .sorted(lambda x: (x.product_id.sequence, x.sequence))
            if pictures:
                rec.picture_id = pictures[0]

    picture_datas = fields.Binary(related='picture_id.datas', string='Picture', readonly=True)
    picture_datas_fname = fields.Char(related='picture_id.datas_fname', readonly=True)

    flat_product_ids = fields.Many2many(comodel_name='lighting.product', compute='_compute_flat_products')

    def _get_flat_products(self):
        self.ensure_one()
        if not self.child_ids:
            return self.product_ids
        else:
            products = self.env['lighting.product']
            for ch in self.child_ids:
                products += ch._get_flat_products()
            return products

    def _compute_flat_products(self):
        for rec in self:
            rec.flat_product_ids = rec._get_flat_products()

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec.flat_product_ids)

    @api.constrains('parent_id')
    def _check_group_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You cannot create recursive groups.'))
        return True

    @api.constrains('parent_id')
    def _check_parent_without_products(self):
        if self.parent_id:
            if self.parent_id.product_ids:
                raise ValidationError(
                    _('Error ! The parent contains products and a parent with products cannot also have childs'))
        return True

    def action_product(self):
        return {
            'name': self.complete_name,
            'type': 'ir.actions.act_window',
            'res_model': 'lighting.product',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('id', 'in', self.flat_product_ids.mapped('id'))],
            'context': {'default_product_group_id': self.id},
        }
