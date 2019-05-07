# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError


class LightingProductReview(models.Model):
    _name = 'lighting.review.package'
    _order = 'name'

    name = fields.Char(required=True)
    description = fields.Text()
    start_date = fields.Date(required=True)
    end_date = fields.Date()

    responsible_ids = fields.Many2many(comodel_name='res.users',
                                       relation='lighting_review_package_user_rel',
                                       string='Responsibles', required=True)

    review_ids = fields.One2many(comodel_name='lighting.product.review',
                                 inverse_name='package_id',
                                 string='Reviews', copy=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The review package name must be unique!'),
                        ]

    product_reviewed_count = fields.Integer(string='Reviewed product(s)', compute='_compute_product_count')
    product_pending_count = fields.Integer(string='Pending product(s)', compute='_compute_product_count')

    def _compute_product_count(self):
        for rec in self:
            rec.product_reviewed_count = len(rec.review_ids.filtered(lambda x: x.reviewed))
            rec.product_pending_count = len(rec.review_ids.filtered(lambda x: not x.reviewed))

    product_reviewed_percent = fields.Float(compute='_compute_product_reviewed_percent', string='% Reviewed')

    def _compute_product_reviewed_percent(self):
        for rec in self:
            product_count = len(rec.review_ids.mapped('product_id'))
            if product_count != 0:
                rec.product_reviewed_percent = rec.product_reviewed_count / product_count * 100

    def action_product_reviewed(self):
        return {
            'name': _('Reviewed products'),
            'type': 'ir.actions.act_window',
            'res_model': 'lighting.product',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('id', 'in', self.review_ids.filtered(lambda x: x.reviewed).mapped('product_id.id'))],
            'context': {'default_review_ids': [(0, False, {'package_id': self.id, 'reviewed': True})]},
        }

    def action_product_pending(self):
        return {
            'name': _('Pending products'),
            'type': 'ir.actions.act_window',
            'res_model': 'lighting.product',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('id', 'in', self.review_ids.filtered(lambda x: not x.reviewed).mapped('product_id.id'))],
            'context': {'default_review_ids': [(0, False, {'package_id': self.id, 'reviewed': False})]},
        }

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {},
                       name=_('%s (copy)') % self.name,
                       )

        return super().copy(default)
