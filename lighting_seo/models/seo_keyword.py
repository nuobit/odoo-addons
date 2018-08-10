# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LightingSEOKeyword(models.Model):
    _name = 'lighting.seo.keyword'
    _order = 'name'

    name = fields.Char(string='Keyword', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The keyword must be unique!'),
                        ]

    product_count = fields.Integer(compute='_compute_counts', string='Product(s)')
    family_count = fields.Integer(compute='_compute_counts', string='Family(s)')
    type_count = fields.Integer(compute='_compute_counts', string='Type(s)')
    application_count = fields.Integer(compute='_compute_counts', string='Application(s)')
    catalog_count = fields.Integer(compute='_compute_counts', string='Catalog(s)')

    def _compute_counts(self):
        maps = [('product_count', 'lighting.product'),
                ('family_count', 'lighting.product.family'),
                ('type_count', 'lighting.product.type'),
                ('application_count', 'lighting.product.application'),
                ('catalog_count', 'lighting.catalog'),
                ]
        for record in self:
            for field, model in maps:
                count = self.env[model].search_count([('seo_keyword_ids', '=', record.id)])
                setattr(record, field, count)

    @api.multi
    def unlink(self):
        models = ['lighting.product', 'lighting.catalog', 'lighting.product.family',
                  'lighting.product.type', 'lighting.product.application']

        for m in models:
            records = self.env[m].search([('seo_keyword_ids', 'in', self.ids)])
            if records:
                raise UserError(_("You are trying to delete a record that is still referenced by '%s' model!" % m))

        return super(LightingSEOKeyword, self).unlink()
