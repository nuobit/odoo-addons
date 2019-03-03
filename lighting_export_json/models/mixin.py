# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields, _


class LightingExportJsonMixin:
    def get_field_d(self, field, template_id, translate=False):
        active_langs = ['en_US', 'es_ES', 'fr_FR']

        ## generem els labels sempre traduits
        label_d = {}
        for lang in active_langs:
            meta = self.with_context(lang=lang).fields_get([field], ['string', 'type', 'selection'])[field]
            if lang not in label_d:
                label_d[lang] = {}

            label_d[lang] = meta['string']

        ## generm, els vlaors traduits en funio del parametre
        value_d = {}
        for lang in active_langs:
            meta = self.with_context(lang=lang).fields_get([field], ['string', 'type', 'selection'])[field]
            datum = getattr(self.with_context(lang=lang), field)
            if meta['type'] == 'selection':
                datum = dict(meta['selection']).get(datum)
            elif meta['type'] == 'boolean':
                if translate:
                    datum = _('Yes') if datum else _('No')
            elif meta['type'] == 'date':
                datum = fields.Date.from_string(datum)
            elif meta['type'] == 'datetime':
                datum = fields.Datetime.from_string(datum)
            elif meta['type'] == 'many2one':
                datum = datum.display_name
            elif meta['type'] == 'many2many':
                datum = [x.display_name for x in datum]
            elif meta['type'] == 'one2many':
                if hasattr(datum, 'export_name'):
                    datum = datum.export_name(template_id)
                else:
                    datum = None  # NOT SUPPORTED

            if meta['type'] != 'boolean' and not datum:
                datum = None

            if translate:
                if datum is not None:
                    value_d[lang] = datum
            else:
                if datum is not None:
                    value_d = datum
                break

        field_d = {}
        if value_d:
            field_d = {
                'label': label_d,
                'value': value_d
            }

        return field_d
