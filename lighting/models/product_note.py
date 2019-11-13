# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductNotes(models.Model):
    _name = 'lighting.product.notes'
    _rec_name = 'note_id'
    _order = 'product_id,sequence desc'

    sequence = fields.Integer(required=True, default=1)

    note_id = fields.Many2one(comodel_name='lighting.product.note',
                              ondelete='restrict', string='Note', required=True)

    product_id = fields.Many2one(comodel_name='lighting.product',
                                 ondelete='cascade', string='Product', required=True)

    _sql_constraints = [('name_uniq', 'unique (product_id,note_id)',
                         "There's notes used more than one time!"),
                        ]


class LightingProductNote(models.Model):
    _name = 'lighting.product.note'
    _order = 'name'

    name = fields.Char(required=True, translate=True)

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product.notes'].search_count([('note_id', '=', record.id)])

    _sql_constraints = [('name_uniq', 'unique (name)', 'The note must be unique!'),
                        ]
