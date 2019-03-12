# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError

import os
import json
import datetime


class LightingExportTemplate(models.Model):
    _inherit = 'lighting.export.template'

    output_type = fields.Selection(selection_add=[('export_product_json', _('Json file (.json)'))])

    pretty_print = fields.Boolean(string="Pretty print", default=True)

    output_base_directory = fields.Char(string="Base directory")
    db_filestore = fields.Boolean(string="Database filestore")
    output_directory = fields.Char(string="Directory")
    output_filename_prefix = fields.Char(string="Filename prefix")

    @api.onchange('db_filestore')
    def onchange_db_filestore(self):
        if self.db_filestore:
            self.output_base_directory = tools.config.filestore(self._cr.dbname)
        else:
            self.output_base_directory = False

    @api.multi
    def action_json_export(self):
        def default(o):
            if isinstance(o, datetime.date):
                return fields.Date.to_string(o)

            if isinstance(o, datetime.datetime):
                return fields.Datetime.to_string(o)

            if isinstance(o, set):
                return sorted(list(o))

        kwargs = {}
        if self.pretty_print:
            kwargs = dict(indent=4, sort_keys=True)

        objects = self.env['lighting.product'].search([], limit=10)
        res = self.generate_data(objects, hide_empty_fields=self.hide_empty_fields)

        for suffix, data in res.items():
            filename = '%s.json' % (self.output_filename_prefix % suffix,)
            parts = [self.output_base_directory]
            if self.output_directory:
                parts.append(self.output_directory)
                os.makedirs(os.path.join(*parts), mode=0o770, exist_ok=True)
            parts.append(filename)
            path = os.path.join(*parts)

            with open(path, 'w') as f:
                json.dump(res[suffix], f, ensure_ascii=False, default=default, **kwargs)

    def generate_data(self, objects, hide_empty_fields=True):
        active_langs = self.lang_ids.mapped('code')

        ## base headers with labels replaced and subset acoridng to template
        header = {}
        for line in self.field_ids.sorted(lambda x: x.sequence):
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
        for obj in objects:
            obj_d = {}
            for field, meta in header.items():
                field_d = {}
                has_value = False
                meta_langs = sorted(meta['string'].keys(), key=lambda x: (0, x) if x == 'en_US' else (1, x))
                for lang in meta_langs:
                    datum = getattr(obj.with_context(lang=lang, template_id=self), field)
                    if meta['type'] == 'selection':
                        datum = dict(meta['selection'][lang]).get(datum)
                    elif meta['type'] == 'boolean':
                        if meta['translate']:
                            datum = _('Yes') if datum else _('No')
                    elif meta['type'] == 'many2many':
                        datum = [x.display_name for x in datum]
                    elif meta['type'] == 'many2one':
                        datum = datum.display_name

                    if meta['type'] != 'boolean' and not datum:
                        datum = None

                    if datum is not None:
                        has_value = True

                    ## acumulem els valors
                    if not meta['translate']:
                        field_d = datum
                        break
                    else:
                        field_d[lang] = datum

                if has_value or not hide_empty_fields:
                    obj_d[field] = field_d

            if obj_d:
                ## afegim l'objecte
                objects_ld.append(obj_d)

        # cerqeum tots el sproductes de nou i generm la llista de tempaltes i les seves variants
        if 'template' in header:
            template_d = {}
            for obj in objects:
                template_name = getattr(obj, 'template', None)
                if template_name:
                    if template_name not in template_d:
                        template_d[template_name] = []
                    template_d[template_name].append(obj)

            # comprovem que les temlates rene  mes dun element, sino, leliminem
            # escollim un objet qualsevol o generalm al descricio sense el finish
            template_clean_d = {}
            for k, v in template_d.items():
                if len(v) > 1:
                    template_desc_d = {}
                    for lang in active_langs:
                        template_desc_d[lang] = v[0].with_context(lang=lang)._generate_description(
                            show_variant_data=False)

                    template_clean_d[k] = {'description': template_desc_d}

        res = {
            'labels': label_d,
            'templates': template_clean_d,
            'products': objects_ld,
        }

        return res
