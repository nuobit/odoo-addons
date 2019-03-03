# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from collections import OrderedDict


class LightingProductBeam(models.Model):
    _inherit = 'lighting.product.beam'

    @api.multi
    def export_name(self, template_id=None):
        valid_field = ['num', 'photometric_distribution_ids', 'dimension_ids']
        res = []
        for rec in self:
            line = OrderedDict()
            for field in valid_field:
                field_meta = self.fields_get([field], ['string', 'type'])[field]
                datum = getattr(rec, field)
                if field_meta['type'] == 'many2one':
                    datum = datum.display_name
                elif field_meta['type'] == 'many2many':
                    datum = ','.join([x.display_name for x in datum])
                elif field_meta['type'] == 'one2many':
                    datum = datum.export_name()
                elif field_meta['type'] == 'date':
                    datum = fields.Date.from_string(datum)

                if field_meta['type'] != 'boolean' and not datum:
                    datum = None

                line[field_meta['string']] = datum

            res.append(line)

        return res
