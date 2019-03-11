# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields, _
from collections import OrderedDict

from .mixin import LightingExportJsonMixin


class LightingProductSource(models.Model, LightingExportJsonMixin):
    _inherit = 'lighting.product.source'

    ## computed fields
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

        # camp wattage
        w_integrated = 0
        wattages_s = set()
        for line in self.mapped('line_ids'):
            if line.wattage:
                wattage = line.wattage * line.source_id.num
                if line.is_integrated:
                    w_integrated += wattage
                else:
                    wattages_s.add(wattage)

        wattages_s2 = set()
        for w in wattages_s:
            wattages_s2.add(w + w_integrated)

        if wattages_s2:
            res['line_ids.wattage'] = sorted(list(wattages_s2))

        # camp temp color
        colork_s = set()
        for line in self.mapped('line_ids'):
            if line.is_integrated:
                if line.color_temperature_id:
                    colork_s.add(line.color_temperature_id.value)

        if colork_s:
            res['line_ids.color_temperature'] = sorted(list(colork_s))

        # camp fluxe
        fluxes_s = set()
        for line in self.mapped('line_ids'):
            if line.is_integrated:
                if line.luminous_flux1:
                    flux1 = line.luminous_flux1 * line.source_id.num
                    fluxes_s.add(flux1)
                if line.luminous_flux2:
                    flux2 = line.luminous_flux2 * line.source_id.num
                    fluxes_s.add(flux2)

        if fluxes_s:
            res['line_ids.luminous_flux'] = sorted(list(fluxes_s))

        # camp tipus font de llum
        if any(self.mapped('line_ids').mapped('is_integrated')):
            source_type = _("LED")
        else:
            source_type = _("Other")

        res['line_ids.type_id.type'] = source_type

        return res
