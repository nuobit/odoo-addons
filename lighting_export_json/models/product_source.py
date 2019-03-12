# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields, _
from collections import OrderedDict


class LightingProductSource(models.Model):
    _inherit = 'lighting.product.source'

    line_full_display = fields.Char(compute='_compute_line_full_display', string="Light source")

    @api.depends('num', 'lampholder_id', 'lampholder_id.code', 'line_ids')
    def _compute_line_full_display(self):
        for rec in self:
            res = []
            if rec.num > 1:
                res.append('%i x' % rec.num)

            if rec.lampholder_id:
                res.append(rec.lampholder_id.code)

            if rec.line_display:
                res.append(rec.line_display)

            if res:
                rec.line_full_display = ' '.join(res)
