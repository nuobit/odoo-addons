# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api

class LightingExportDimension():

    @api.multi
    def export_name(self):
        if not self:
            return None

        same_uom = True
        uoms = set()
        for rec in self:
            if rec.type_id.uom not in uoms:
                if not uoms:
                    uoms.add(rec.type_id.uom)
                else:
                    same_uom = False
                    break

        res_label = ' x '.join(['%s' % x.type_id.name for x in self])
        res_value = ' x '.join(['%g' % x.value for x in self])

        if same_uom:
            res_label = '%s (%s)' % (res_label, uoms.pop())
        else:
            res_value = ' x '.join(['%g%s' % (x.value, x.type_id.uom) for x in self])

        return '%s: %s' % (res_label, res_value)
