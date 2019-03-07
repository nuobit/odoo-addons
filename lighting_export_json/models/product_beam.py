# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields, _
from collections import OrderedDict

from .mixin import LightingExportJsonMixin


class LightingProductBeam(models.Model, LightingExportJsonMixin):
    _inherit = 'lighting.product.beam'

    line_full_display = fields.Char(compute='_compute_line_full_display', string="Description")

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

    @api.multi
    def export_json(self, template_id=None):
        valid_field = ['sequence', 'line_full_display']
        translate_field = ['line_full_display']
        res = []
        for rec in self.sorted(lambda x: x.sequence):
            line = OrderedDict()
            for field in valid_field:
                field_d = rec.get_field_d(field, template_id, translate=field in translate_field)
                if field_d:
                    line[field] = field_d['value']

            if line:
                res.append(line)

        return res

    @api.multi
    def export_search_json(self, template_id=None):
        res = {}

        #### primer camp
        field1 = 'dimension_ids'
        field2 = 'value'
        for rec in self:
            values = getattr(rec, field1).filtered(lambda x: getattr(x, field2)).mapped(field2)
            if values:
                key = '.'.join([field1, field2])
                if key not in res:
                    res[key] = set()
                res[key] |= set(values)

        return res
