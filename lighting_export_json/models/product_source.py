# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields, _
from collections import OrderedDict


class LightingProductSource(models.Model):
    _inherit = 'lighting.product.source'

    def get_source_type(self):
        res = []
        for src in self.sorted(lambda x: ({'main': 0, 'aux': 1}[x.relevance], x.sequence)):
            s = []
            if src.lampholder_id:
                s.append(src.lampholder_id.display_name)

            src_t = src.line_ids.get_source_type()
            if src_t:
                s.append('/'.join(src_t))

            s_l = None
            if s:
                s_l = ' '.join(s)
            res.append(s_l)

        if not any(res):
            return None
        return res

    def get_color_temperature(self):
        res = []
        for src in self.sorted(lambda x: ({'main': 0, 'aux': 1}[x.relevance], x.sequence)):
            src_k = src.line_ids.get_color_temperature()
            k_l = None
            if src_k:
                k_l = '/'.join(src_k)
            res.append(k_l)

        if not any(res):
            return None
        return res

    def get_luminous_flux(self):
        res = []
        for src in self.sorted(lambda x: ({'main': 0, 'aux': 1}[x.relevance], x.sequence)):
            src_k = src.line_ids.get_luminous_flux()
            k_l = None
            if src_k:
                kn_l = []
                if src.num > 1:
                    kn_l.append('%ix' % src.num)
                kn_l.append('/'.join(src_k))
                k_l = ' '.join(kn_l)
            res.append(k_l)

        if not any(res):
            return None
        return res

    def get_wattage(self):
        res = []
        for src in self.sorted(lambda x: ({'main': 0, 'aux': 1}[x.relevance], x.sequence)):
            src_k = src.line_ids.get_wattage()
            if src_k:
                kn_l = []
                if src.num > 1:
                    kn_l.append('%ix' % src.num)
                kn_l.append(src_k)
                src_k = ' '.join(kn_l)
            res.append(src_k)

        if not any(res):
            return None
        return res


class LightingProductSourceLine(models.Model):
    _inherit = 'lighting.product.source.line'

    def get_source_type(self):
        res = self.sorted(lambda x: x.sequence) \
            .mapped('type_id.display_name')
        if not res:
            return None
        return res

    def get_color_temperature(self):
        res = self.sorted(lambda x: x.sequence) \
            .mapped('color_temperature_id.display_name')
        if not res:
            return None
        return res

    def get_luminous_flux(self):
        res = []
        for line in self.sorted(lambda x: x.sequence):
            lm_l = ['%iLm' % x for x in
                    filter(lambda x: x, [line.luminous_flux1, line.luminous_flux2])]
            if lm_l:
                res.append('-'.join(lm_l))

        if not res:
            return None
        return res

    def get_wattage(self):
        w_d = {}
        for rec in self:
            if rec.wattage:
                if rec.wattage_magnitude not in w_d:
                    w_d[rec.wattage_magnitude] = []
                w_d[rec.wattage_magnitude].append(rec.wattage)

        if not w_d:
            return None

        wattage_magnitude_option = dict(
            self.fields_get(['wattage_magnitude'], ['selection'])
                .get('wattage_magnitude').get('selection'))

        w_l = []
        for wm, wv_l in w_d.items():
            ws = wattage_magnitude_option.get(wm)
            w_l.append('%g%s' % (max(wv_l), ws))

        return '%s %s' % ('/'.join(w_l), _('max.'))
