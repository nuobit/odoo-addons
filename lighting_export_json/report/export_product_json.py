# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, models, fields
from odoo.exceptions import UserError, ValidationError

import datetime

import json
import re


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

        ### afegim els labels
        label_d = {}
        for field, meta in header.items():
            label_d[field] = meta['string']

        ## generate data and gather data
        objects_ld = []
        template_d = {}
        for obj in objects:
            obj_d = {}
            search_d = {}
            for field, meta in header.items():
                field_d = {}
                has_value = False
                meta_langs = sorted(meta['string'].keys(), key=lambda x: (0, x) if x == 'en_US' else (1, x))
                for lang in meta_langs:
                    datum = getattr(obj.with_context(lang=lang), field)
                    search = None
                    if meta['type'] == 'selection':
                        datum = dict(meta['selection'][lang]).get(datum)
                    elif meta['type'] == 'boolean':
                        if meta['translate']:
                            datum = _('Yes') if datum else _('No')
                    elif meta['type'] == 'many2many':
                        if hasattr(datum, 'export_search_json'):
                            search = datum.export_search_json(template_id)

                        datum = [x.display_name for x in datum]
                    elif meta['type'] == 'many2one':
                        datum = datum.display_name
                    elif meta['type'] == 'one2many':
                        if hasattr(datum, 'export_search_json'):
                            search = datum.export_search_json(template_id)

                        if hasattr(datum, 'export_json'):
                            datum = datum.export_json(template_id)
                        else:
                            datum = None  # NOT SUPPORTED

                    if meta['type'] != 'boolean' and not datum:
                        datum = None

                    if datum is not None:
                        has_value = True

                    ## calculem els search
                    if search:
                        for k, v in search.items():
                            key = '.'.join([field, k])
                            if not meta['translate']:
                                if key not in search_d:
                                    search_d[key] = v
                            else:
                                if key not in search_d:
                                    search_d[key] = {}
                                if lang not in search_d[key]:
                                    search_d[key][lang] = v

                    ## acumulem els valors
                    if not meta['translate']:
                        #field_d['value'] = datum
                        field_d = datum
                        break
                    else:
                        #if 'value' not in field_d:
                        #    field_d['value'] = {}
                        field_d[lang] = datum

                if has_value or not data.get('hide_empty_fields'):
                    ## afegim els labels
                    # for lang in meta['string'].keys():
                    #     if 'label' not in field_d:
                    #         field_d['label'] = {}
                    #     field_d['label'][lang] = meta['string'][lang]

                    # afegim les dades
                    obj_d[field] = field_d

            if obj_d:
                # afegim els searchs
                if search_d:
                    for k, v in search_d.items():
                        obj_d['search_%s' % k] = v

                ## afegim a les variants
                reference = obj_d['reference']
                m = re.match(r'^(.+)-.{2}$', reference)
                if m:
                    template_name = m.group(1)
                    if template_name not in template_d:
                        template_d[template_name] = []
                    template_d[template_name].append(reference)

                    ## afegim el pare a la ref actual
                    obj_d['template'] = template_name

                ## afegim l'obkecte
                objects_ld.append(obj_d)

        # comprovem que les temlates rene  mes dun element, sino, leliminem
        template_clean_d = {}
        for k, v in template_d.items():
            if len(v) > 1:
                template_clean_d[k] = v

        # eliminem el camp tempalte dels productes que nomes tenen un pare
        # vol dir que no te variants o en te 1 i es el propi pare
        # afegim la descriocio generica (sens el finish) a la template
        template_upd_d = {}
        for obj_d in objects_ld:
            if 'template' in obj_d:
                if obj_d['template'] in template_clean_d:
                    template_upd_d = {
                        'reference': obj_d['template'],
                    }
                    if 'description' not in template_upd_d:
                        template_upd_d['description'] = obj_d['description']

        def default(o):
            if isinstance(o, datetime.date):
                return fields.Date.to_string(o)

            if isinstance(o, datetime.datetime):
                return fields.Datetime.to_string(o)

            if isinstance(o, set):
                return sorted(list(o))

        kwargs = {}
        if data['pretty_print']:
            kwargs = dict(indent=4, sort_keys=True)

        json_data = {
            'labels': label_d,
            'templates': template_upd_d,
            'products': objects_ld,
        }

        return json.dumps(json_data, ensure_ascii=False, default=default, **kwargs)
