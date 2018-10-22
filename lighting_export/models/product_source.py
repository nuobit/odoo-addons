# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields


class LightingProductSource(models.Model):
    _inherit = 'lighting.product.source'

    @api.multi
    def export_name(self, template_id=None):
        valid_field = ['relevance', 'num', 'lampholder_id', 'line_display', 'line_ids']
        res = []
        for rec in self.sorted(lambda x: x.sequence):
            line = []
            for field in valid_field:
                field_meta = self.fields_get([field], ['string', 'type', 'selection'])[field]
                datum = getattr(rec, field)
                if field_meta['type'] == 'selection':
                    datum = dict(field_meta['selection']).get(datum)
                elif field_meta['type'] == 'many2one':
                    datum = datum.display_name
                elif field_meta['type'] == 'many2many':
                    datum = ','.join([x.display_name for x in datum])
                elif field_meta['type'] == 'one2many':
                    datum = datum.export_name()
                elif field_meta['type'] == 'date':
                    datum = fields.Date.from_string(datum)

                if field_meta['type'] != 'boolean' and not datum:
                    datum = None

                if not isinstance(datum, (tuple, list)):
                    datum = [(field_meta['string'], datum)]

                line += datum

            res.append(line)

        return res


class LightingProductSourceLine(models.Model):
    _inherit = 'lighting.product.source.line'

    @api.multi
    def export_name(self, template_id=None):
        res = []

        field = 'color_temperature'
        metas = self.fields_get([field], ['string', 'type', 'selection'])
        field_data0 = [getattr(rec, field) for rec in self.sorted(lambda x: x.sequence) if getattr(rec, field)!=0 ]
        if len(field_data0) == 1:
            field_data = field_data0[0]
        else:
            field_data = ' / '.join(map(lambda x: '%i' % x, field_data0))
        res.append((metas[field]['string'], field_data))

        field = 'luminous_flux1'
        metas = self.fields_get([field], ['string', 'type', 'selection'])
        field_data0 = [rec.luminous_flux_display for rec in self.sorted(lambda x: x.sequence) if rec.luminous_flux_display]
        if len(field_data0) == 1:
            field_data = field_data0[0]
            try:
                field_data = int(field_data)
            except ValueError:
                pass
        else:
            field_data = ' / '.join(field_data0)
        res.append((metas[field]['string'], field_data))

        return res

