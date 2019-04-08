# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError

import os
import json
import datetime
import ast

import logging

_logger = logging.getLogger(__name__)


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

        domain = []
        if self.domain:
            domain = ast.literal_eval(self.domain)

        objects = self.env['lighting.product'].search(domain)
        res = self.generate_data(objects, hide_empty_fields=self.hide_empty_fields)

        today_str = fields.Date.from_string(fields.Date.context_today(self)).strftime('%Y%m%d')
        for suffix, data in res.items():
            base_filename = self.output_filename_prefix % dict(object=suffix, date=today_str)
            filename = '%s.json' % base_filename
            parts = [self.output_base_directory]
            if self.output_directory:
                parts.append(self.output_directory)
                os.makedirs(os.path.join(*parts), mode=0o774, exist_ok=True)
            parts.append(filename)
            path = os.path.join(*parts)

            with open(path, 'w') as f:
                json.dump(res[suffix], f, ensure_ascii=False, default=default, **kwargs)

    def generate_data(self, objects, hide_empty_fields=True):
        _logger.info("Export data started...")
        active_langs = self.lang_ids.mapped('code')

        res = {}
        ## base headers with labels replaced and subset acoridng to template
        _logger.info("Generating product headers...")
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
        _logger.info("Product headers successfully generated...")

        ### afegim els labels
        _logger.info("Generating product labels...")
        label_d = {}
        for field, meta in header.items():
            label_d[field] = meta['string']
        if label_d:
            res.update({'labels': label_d})
        _logger.info("Product labels successfully generated...")

        ## generate data and gather data
        _logger.info("Generating products...")
        n = len(objects)
        th = int(n / 100) or 1
        objects_ld = []
        for i, obj in enumerate(objects, 1):
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
                objects_ld.append(obj_d)

            if (i % th) == 0:
                _logger.info(" - Progress products generation %i%%" % (int(i / n * 100)))

        if objects_ld:
            res.update({'products': objects_ld})
        _logger.info("Products successfully generated...")

        # cerqeum tots el sproductes de nou i generm la llista de tempaltes i les seves variant
        if 'template' in header:
            _logger.info("Generating product virtual data...")
            template_d = {}
            for obj in objects:
                template_name = getattr(obj, 'template', None)
                if template_name:
                    if template_name not in template_d:
                        template_d[template_name] = []
                    template_d[template_name].append(obj)

            # generem els bundles agrupant cada bundle i posant dins tots els tempaltes
            # dels requireds associats
            bundle_d = {}
            for template_name, objects_l in template_d.items():
                products = self.env['lighting.product'].browse([x.id for x in objects_l])
                is_bundle_template = any(products.mapped('is_bundle'))
                if is_bundle_template:
                    products_required = products.mapped('required_ids')
                    if products_required:
                        ## components
                        bundle_d[template_name] = {
                            'templates': sorted(list(set(products_required.mapped('template'))))
                        }

                        ## default attach
                        # first own attachments
                        attachment_ids = products.mapped('attachment_ids') \
                            .filtered(lambda x: x.is_bundle_default and
                                                x.type_id.id in self.attachment_ids.mapped('type_id.id')) \
                            .sorted(lambda x: (x.sequence, x.id))

                        # after required attachments
                        if not attachment_ids:
                            attachment_ids = products_required.mapped('attachment_ids') \
                                .filtered(lambda x: x.is_bundle_default and
                                                    x.type_id.id in self.attachment_ids.mapped('type_id.id')) \
                                .sorted(lambda x: (x.sequence, x.id))

                        if attachment_ids:
                            bundle_d[template_name].update({
                                'attachment': {
                                    'datas_fname': attachment_ids[0].datas_fname,
                                    'store_fname': attachment_ids[0].attachment_id.store_fname,
                                }
                            })

            if bundle_d:
                res.update({'bundles': bundle_d})

            # comprovem que les temlates rene  mes dun element, sino, leliminem
            # escollim un objet qualsevol o generalm al descricio sense el finish
            template_clean_d = {}
            for k, v in template_d.items():
                if len(v) > 1:
                    ## description
                    template_desc_d = {}
                    for lang in active_langs:
                        lang_description = v[0].with_context(lang=lang)._generate_description(
                            show_variant_data=False)
                        if lang_description:
                            template_desc_d[lang] = lang_description
                    if template_desc_d:
                        if k not in template_clean_d:
                            template_clean_d[k] = {}
                        template_clean_d[k].update({
                            'description': template_desc_d
                        })

                    ## default attach
                    products = self.env['lighting.product'].browse([p.id for p in v])
                    attachment_ids = products.mapped('attachment_ids') \
                        .filtered(lambda x: x.is_template_default and
                                            x.type_id.id in self.attachment_ids.mapped('type_id.id')) \
                        .sorted(lambda x: (x.sequence, x.id))
                    if attachment_ids:
                        if k not in template_clean_d:
                            template_clean_d[k] = {}
                        template_clean_d[k].update({
                            'attachment': {
                                'datas_fname': attachment_ids[0].datas_fname,
                                'store_fname': attachment_ids[0].attachment_id.store_fname,
                            }
                        })
            if template_clean_d:
                res.update({'templates': template_clean_d})

            _logger.info("Product virtual data successfully generated...")

        if objects_ld:
            ## generm la informacio de les families
            _logger.info("Generating family data...")
            # obtenim els ids de es fmailie sel sobjectes seleccionats
            families = objects.mapped('family_ids')
            if families:
                family_ld = []
                for family in families.sorted(lambda x: x.sequence):
                    family_d = {}
                    # descricpio llarga
                    family_descr_lang = {}
                    for lang in active_langs:
                        descr = family.with_context(lang=lang).description
                        if descr:
                            family_descr_lang[lang] = descr
                    if family_descr_lang:
                        family_d.update({
                            'description': family_descr_lang,
                        })
                    # adjunts ordenats
                    if family.attachment_ids:
                        attachments = family.attachment_ids \
                            .filtered(lambda x: x.is_default) \
                            .sorted(lambda x: (x.sequence, x.id))
                        if attachments:
                            family_d.update({
                                'attachment': {
                                    'datas_fname': attachments[0].datas_fname,
                                    'store_fname': attachments[0].attachment_id.store_fname,
                                },
                            })

                    # nom: si la familia te dades, afegim el nom i lafegim, sino no
                    if family_d:
                        family_d.update({
                            'name': family.name,
                        })
                        family_ld.append(family_d)

                if family_ld:
                    res.update({'families': family_ld})

            _logger.info("Family data successfully generated...")

            ## generm la informacio de les aplicacions
            _logger.info("Generating application data...")
            applications = objects.mapped('application_ids')
            if applications:
                application_ld = []
                for application in applications.sorted(lambda x: x.sequence):
                    application_d = {}
                    # adjunts ordenats
                    if application.attachment_ids:
                        attachments = application.attachment_ids \
                            .filtered(lambda x: x.is_default) \
                            .sorted(lambda x: (x.sequence, x.id))
                        if attachments:
                            application_d.update({
                                'attachment': {
                                    'datas_fname': attachments[0].datas_fname,
                                    'store_fname': attachments[0].attachment_id.store_fname,
                                },
                            })

                    # nom: si la aplicacio te dades, afegim el nom i lafegim, sino no
                    if application_d:
                        application_d.update({
                            'name': application.name,
                        })
                        application_ld.append(application_d)

                if application_ld:
                    res.update({'applications': application_ld})

            _logger.info("Application data successfully generated...")

        _logger.info("Export data successfully done")

        return res
