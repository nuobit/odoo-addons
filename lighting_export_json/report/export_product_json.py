# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, models, fields
from odoo.exceptions import UserError, ValidationError

import datetime

import json


class ExportProductJson(models.AbstractModel):
    _name = 'report.lighting_export_json.export_product_json'
    _inherit = 'report.report_json.abstract'

    def generate_json_report(self, data, objects):
        return self.with_context(lang=data['lang']).generate_json_report_ctx(data, objects)

    def generate_json_report_ctx(self, data, objects):
        template_id = self.env['lighting.export.template'].browse(data.get('template_id'))
        objects = self.env['lighting.product'].browse(data.get('active_ids'))
        if data.get('interval') == 'all':
            active_model = self.env.context.get('active_model')
            active_domain = data.get('context').get('active_domain')
            objects = self.env[active_model].search(active_domain)

        active_langs = self.env['res.lang'].search([('active', '=', True)]).mapped("code")
        active_langs = ['en_US', 'es_ES', 'fr_FR']
        # active_langs.sort(lambda x: (0, x) if x == 'en_US' else (1, x))

        ## base headers with labels replaced and subset acoridng to template
        header = {}
        for line in template_id.field_ids.sorted(lambda x: x.sequence):
            field_name = line.field_id.name
            item = {}
            for lang in active_langs:
                item_lang = objects.with_context(lang=lang).fields_get([field_name],
                                                                       ['type', 'string', 'selection'])
                if item_lang:
                    meta = item_lang[field_name]
                    for k, v in meta.items():
                        if k in ('type',):
                            if k not in item:
                                item[k] = v
                        else:
                            if k == 'string':
                                line_lang = line.with_context(lang=lang)
                                if line_lang.label and line_lang.label.strip():
                                    v = line_lang.label

                            if k not in item:
                                item[k] = {}

                            item[k][lang] = v
            if item:
                item['translate'] = line.translate
                header[field_name] = item

        ## generate data and gather header data
        objects_ld = []
        for obj in objects:
            obj_d = {}
            for field, meta in header.items():
                field_d = {}
                has_value = False
                meta_langs = sorted(meta['string'].keys(), key=lambda x: (0, x) if x == 'en_US' else (1, x))
                for lang in meta_langs:
                    datum = getattr(obj.with_context(lang=lang), field)
                    if meta['type'] == 'selection':
                        datum = dict(meta['selection'][lang]).get(datum)
                    elif meta['type'] == 'boolean':
                        if meta['translate']:
                            datum = _('Yes') if datum else _('No')
                    elif meta['type'] == 'many2many':
                        datum = [x.display_name for x in datum]
                    elif meta['type'] == 'many2one':
                        datum = datum.display_name
                    elif meta['type'] == 'one2many':
                        if hasattr(datum, 'export_name'):
                            datum = datum.export_name(template_id)
                        else:
                            datum = None  # NOT SUPPORTED

                    if meta['type'] != 'boolean' and not datum:
                        datum = None

                    if datum is not None:
                        has_value = True

                    if not meta['translate']:
                        field_d['value'] = datum
                        break
                    else:
                        if 'value' not in field_d:
                            field_d['value'] = {}
                        field_d['value'][lang] = datum

                if has_value or not data.get('hide_empty_fields'):
                    ## afegim els labels
                    for lang in meta['string'].keys():
                        if 'label' not in field_d:
                            field_d['label'] = {}
                        field_d['label'][lang] = meta['string'][lang]

                    obj_d[field] = field_d

            if obj_d:
                objects_ld.append(obj_d)

        def default(o):
            if isinstance(o, datetime.date):
                return fields.Date.to_string(o)

            if isinstance(o, datetime.datetime):
                return fields.Datetime.to_string(o)

        return json.dumps(objects_ld, ensure_ascii=False, default=default, indent=4, sort_keys=True)
