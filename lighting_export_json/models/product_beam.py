# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields, _


class LightingProductBeam(models.Model):
    _inherit = 'lighting.product.beam'

    line_full_display = fields.Char(compute='_compute_line_full_display')

    @api.depends('num', 'photometric_distribution_ids', 'dimension_ids')
    def _compute_line_full_display(self):
        for rec in self:
            res = []
            if rec.num > 1:
                res.append('%i x' % rec.num)

            if rec.photometric_distribution_ids:
                res.append('[%s]' % ', '.join([x.display_name for x in rec.photometric_distribution_ids]))

            if rec.dimensions_display:
                res.append(rec.dimensions_display)

            if res:
                rec.line_full_display = ' '.join(res)
