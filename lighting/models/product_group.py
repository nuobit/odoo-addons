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

    @api.model
    def _get_domain(self):
        model_id = self.env.ref('lighting.model_lighting_product').id
        return [('model_id', '=', model_id)]

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

    ## attributes
    use_category_attributes = fields.Boolean(string='Use category attributes', track_visibility='onchange')
    group_attribute_ids = fields.Many2many(comodel_name='ir.model.fields',
                                           relation='lighting_product_group_field_attribute_rel',
                                           column1='group_id', column2='field_id',
                                           domain=_get_domain,
                                           string='Attributes',
                                           track_visibility='onchange')

    attribute_ids = fields.Many2many(comodel_name='ir.model.fields',
                                     string='Attributes',
                                     readonly=True,
                                     compute='_compute_attributes')

    def _compute_attributes(self):
        for rec in self:
            if not rec.use_category_attributes:
                rec.attribute_ids = rec.group_attribute_ids
            else:
                rec.attribute_ids = [
                    (6, False, [x.id for x in rec.flat_product_ids.mapped('category_id.attribute_ids')])]

    ## common fields
    use_category_fields = fields.Boolean(string='Use category fields', track_visibility='onchange')
    group_field_ids = fields.Many2many(comodel_name='ir.model.fields',
                                       relation='lighting_product_group_field_field_rel',
                                       column1='group_id', column2='field_id',
                                       domain=_get_domain,
                                       string='Fields',
                                       track_visibility='onchange')

    field_ids = fields.Many2many(comodel_name='ir.model.fields',
                                 string='Fields',
                                 readonly=True,
                                 compute='_compute_fields')

    def _compute_fields(self):
        for rec in self:
            if not rec.use_category_fields:
                rec.field_ids = rec.group_field_ids
            else:
                rec.field_ids = [
                    (6, False, [x.id for x in rec.flat_product_ids.mapped('category_id.field_ids')])]

    product_ids = fields.One2many(comodel_name='lighting.product',
                                  inverse_name='product_group_id', string='Products')

    product_count = fields.Integer(compute='_compute_product_count', string='Products')

    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec.product_ids)

    parent_id = fields.Many2one(comodel_name='lighting.product.group', string='Parent',
                                index=True, ondelete='cascade', track_visibility='onchange')
    child_ids = fields.One2many(comodel_name='lighting.product.group', inverse_name='parent_id',
                                string='Child Groups', track_visibility='onchange')

    level = fields.Integer(string='Level', readonly=True, compute='_compute_level')

    def _get_level(self):
        self.ensure_one()
        if not self.parent_id:
            return 0
        else:
            return self.parent_id._get_level() + 1

    def _compute_level(self):
        for rec in self:
            rec.level = rec._get_level()

    has_childs = fields.Boolean(string='Has childs', compute='_compute_has_childs')

    def _compute_has_childs(self):
        for rec in self:
            rec.has_childs = bool(rec.child_ids)

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

    flat_product_count = fields.Integer(compute='_compute_flat_product_count', string='Products (flat)')

    def _compute_flat_product_count(self):
        for rec in self:
            rec.flat_product_count = len(rec.flat_product_ids)

    grouped_product_ids = fields.Many2many(comodel_name='lighting.product', compute='_compute_grouped_products')

    def _get_grouped_products(self):
        self.ensure_one()
        products = self.env['lighting.product']
        if not self.child_ids:
            if self.product_ids:
                products = self.product_ids.sorted(lambda x: x.sequence)[0]
        else:
            for ch in self.child_ids:
                products += ch._get_grouped_products()

        return products

    def _compute_grouped_products(self):
        for rec in self:
            rec.grouped_product_ids = rec._get_grouped_products()

    grouped_product_count = fields.Integer(compute='_compute_grouped_product_count', string='Products (grpd.)')

    def _compute_grouped_product_count(self):
        for rec in self:
            rec.grouped_product_count = len(rec.grouped_product_ids)

    common_product_id = fields.Many2one(comodel_name='lighting.product', readonly=True,
                                        compute='_compute_common_product')

    def _compute_common_product(self):
        for rec in self:
            if rec.grouped_product_ids:
                rec.common_product_id = rec.grouped_product_ids.sorted(lambda x: x.sequence)[0]

    picture_id = fields.Many2one(comodel_name='lighting.attachment',
                                 compute='_compute_attachment')

    def _compute_attachment(self):
        for rec in self:
            pictures = rec.common_product_id.attachment_ids \
                .filtered(lambda x: x.type_id.code == 'F') \
                .sorted(lambda x: (x.product_id.sequence, x.sequence))
            if pictures:
                rec.picture_id = pictures[0]

    picture_datas = fields.Binary(related='picture_id.datas', string='Picture', readonly=True)
    picture_datas_fname = fields.Char(related='picture_id.datas_fname', readonly=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The name must be unique!'),
                        ]

    @api.onchange('use_category_attributes')
    def onchange_use_category_attributes(self):
        if self.use_category_attributes:
            self.attribute_ids = False

    @api.onchange('use_category_fields')
    def onchange_use_fields_attributes(self):
        if self.use_category_fields:
            self.field_ids = False

    @api.constrains('use_category_attributes', 'use_category_fields', 'product_ids', 'product_ids.category_id')
    def _check_category_coherence(self):
        if self.use_category_attributes or self.use_category_fields:
            if not self.flat_product_ids:
                raise ValidationError(_('This group has no products to get the atributes from its categories. '
                                        'Please add some products before enabling '
                                        'the "Use category attributes" or "Use category fields" options.'))
            unique_categories = set()
            for fp in self.flat_product_ids:
                if not fp.category_id:
                    raise ValidationError(_('Unexpected. The product %s has no category defined') % fp.reference)
                unique_categories.add(fp.category_id.id)
            if len(unique_categories) == 0:
                raise ValidationError(_('Unexpected, The products of this group has no categories defined'))
            elif len(unique_categories) > 1:
                raise ValidationError(_('To use the options "Use category attributes" or "Use category fields", '
                                        'all the products must have the same category'))

        return True

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
            'name': _('Products of %s') % self.complete_name,
            'type': 'ir.actions.act_window',
            'res_model': 'lighting.product',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('id', 'in', self.product_ids.mapped('id'))],
            'context': {'default_product_group_id': self.id},
        }

    def action_flat_product(self):
        return {
            'name': _('Flat products below %s') % self.complete_name,
            'type': 'ir.actions.act_window',
            'res_model': 'lighting.product',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('id', 'in', self.flat_product_ids.mapped('id'))],
            'context': {'default_product_group_id': self.id},
        }

    def action_grouped_product(self):
        return {
            'name': _('Grouped products of %s') % self.complete_name,
            'type': 'ir.actions.act_window',
            'res_model': 'lighting.product',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('id', 'in', self.grouped_product_ids.mapped('id'))],
            'context': {'default_product_group_id': self.id},
        }

    def action_common_product(self):
        return {
            'name': _('Common product of %s') % self.complete_name,
            'type': 'ir.actions.act_window',
            'res_model': 'lighting.product',
            'views': [(False, 'form')],
            'view_type': 'form',
            'res_id': self.common_product_id.id,
            'context': {'default_product_group_id': self.id},
        }

    test_output = fields.Text(readonly=True)

    def run_test(self):
        a = []
        for p in self.grouped_product_ids:
            p_d = {}
            for attr in self.attribute_ids:
                # p = p.with_context(lang='fr_FR')
                p_d[attr.name] = getattr(p, attr.name)
            a.append({p.reference: p_d})

        t = {self.name: a}
        import json
        kwargs = dict(indent=4, sort_keys=True)
        self.test_output = json.dumps(t, ensure_ascii=False, **kwargs)
