# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields, _


class LightingProductBeam(models.Model):
    _inherit = 'lighting.product.beam'

    def get_beam(self):
        res = []
        for rec in self.sorted(lambda x: x.sequence):
            bm = []
            if rec.num > 1:
                bm.append('%ix' % rec.num)

            if rec.photometric_distribution_ids:
                bm.append(', '.join([x.display_name for x in rec.photometric_distribution_ids]))

            dimension_display = rec.dimension_ids.get_display()
            if dimension_display:
                bm.append(dimension_display)

            if bm:
                res.append(' '.join(bm))

        if not any(res):
            return None
        return res

    def get_beam_angle(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            angl = []
            for d in src.dimension_ids.sorted(lambda x: x.sequence):
                if d.value and d.type_id.uom == 'º':
                    angl.append('%g%s' % (d.value, d.type_id.uom))
            ang_v = None
            if angl:
                ang_v = '/'.join(angl)
            res.append(ang_v)

        if not any(res):
            return None
        return res
