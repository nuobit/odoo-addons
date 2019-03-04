# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from collections import OrderedDict


class LightingProductSource(models.Model):
    _inherit = 'lighting.product.source'

    @api.multi
    def export_name(self, template_id=None):
        valid_field = ['relevance', 'num', 'lampholder_id', 'line_display']
        res = []
        for rec in self.sorted(lambda x: x.sequence):
            line = OrderedDict()
            for field in valid_field:
                field_meta = self.fields_get([field], ['string', 'type', 'selection'])[field]
                datum = getattr(rec, field)
                if field_meta['type'] == 'selection':
                    datum = dict(field_meta['selection']).get(datum)
                elif field_meta['type'] == 'many2one':
                    datum = datum.display_name
                elif field_meta['type'] == 'many2many':
                    datum = ','.join([x.display_name for x in datum])
                elif field_meta['type'] == 'date':
                    datum = fields.Date.from_string(datum)

                if field_meta['type'] != 'boolean' and not datum:
                    datum = None

                if not isinstance(datum, OrderedDict):
                    datum = OrderedDict([(field_meta['string'], datum)])

                line.update(datum)

            res.append(line)

        return res

