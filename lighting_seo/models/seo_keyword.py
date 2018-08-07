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

    @api.multi
    def unlink(self):
        models = ['lighting.product', 'lighting.product.family',
                  'lighting.product.type', 'lighting.product.application']

        for m in models:
            records = self.env[m].search([('seo_keyword_ids', 'in', self.ids)])
            if records:
                raise UserError(_("You are trying to delete a record that is still referenced by '%s' model!" % m))

        return super(LightingSEOKeyword, self).unlink()