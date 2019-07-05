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

    auto_execute = fields.Boolean("Auto execute")

    @api.onchange('db_filestore')
    def onchange_db_filestore(self):
        if self.db_filestore:
            self.output_base_directory = tools.config.filestore(self._cr.dbname)
        else:
            self.output_base_directory = False

    @api.model
    def autoexecute(self):
        for t in self.env[self._name].search([('auto_execute', '=', True)]):
            t.action_json_export()

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
                json.dump(data, f, ensure_ascii=False, default=default, **kwargs)

    def get_efective_field_name(self, field_name):
        field = self.field_ids.filtered(lambda x: x.field_name == field_name)
        if not field:
            raise Exception("Unexpected, the field %s is not defined on template" % field_name)
        if field.effective_field_name:
            return field.effective_field_name

        return field_name

    def generate_dict(self, obj, header, hide_empty_fields=True):
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
                elif meta['type'] in ('one2many', 'many2many'):
                    datum = [getattr(x, meta['subfield'] or 'display_name') for x in datum]
                elif meta['type'] == 'many2one':
                    datum = getattr(datum, meta['subfield'] or 'display_name')

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
                if meta['effective_field_name']:
                    field = meta['effective_field_name']
                obj_d[field] = field_d

        return obj_d

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
                item['effective_field_name'] = line.effective_field_name
                item['subfield'] = line.subfield_name
                item['translate'] = line.translate
                header[field_name] = item
        _logger.info("Product headers successfully generated.")

        ### afegim els labels
        _logger.info("Generating product labels...")
        label_d = {}
        for field, meta in header.items():
            if meta['effective_field_name']:
                field = meta['effective_field_name']
            label_d[field] = meta['string']
        res.update({'labels': label_d})
        _logger.info("Product labels successfully generated.")

        ## generate data and gather data
        _logger.info("Generating products...")
        n = len(objects)
        th = int(n / 100) or 1
        objects_ld = []
        for i, obj in enumerate(objects, 1):
            obj_d = self.generate_dict(obj, header, hide_empty_fields)
            if obj_d:
                objects_ld.append(obj_d)

            if (i % th) == 0:
                _logger.info(" - Progress products generation %i%%" % (int(i / n * 100)))

        res.update({'products': objects_ld})
        _logger.info("Products successfully generated...")

        _logger.info("Generating dictionary of products...")
        objects_d = {}
        for obj in objects_ld:
            key = obj['reference']
            if key in objects_d:
                raise Exception("Unexpected!! The key %s is duplicated!" % key)
            objects_d[key] = obj
        _logger.info("Dictionary of products successfully generated.")

        # clasiiquem esl grups per nivell
        _logger.info("Classifying Groups by level...")

        def group_classify(groups_d, group, child):
            if group.level not in groups_d:
                groups_d[group.level] = {}

            if group not in groups_d[group.level]:
                groups_d[group.level][group] = {}

            groups_d[group.level][group].update(child)

            if not group.child_ids:  # is a LEAF
                child0 = list(child.keys())[0]
            else:
                child0 = list(child.values())[0]

            if group.parent_id:
                group_classify(groups_d, group.parent_id, {group: child0})

        group_hierarchy_d = {}
        for obj in objects:
            if obj.product_group_id:
                group_classify(group_hierarchy_d, obj.product_group_id, {obj: None})
        _logger.info("Groups successfully classificated by level.")

        ## generem les dades de cada nivell
        _logger.info("Generating Group data....")
        group_data_d = {}
        for level, group_d in group_hierarchy_d.items():
            if level not in group_data_d:
                group_data_d[level] = {}

            for group, childs in group_d.items():
                ## calculem els camp comuns
                k, v = list(childs.items())[0]
                product = v or k

                product_data = {}
                fields = [self.get_efective_field_name(x.name) for x in group.field_ids]
                for f in fields:
                    if f in objects_d[product.reference]:
                        product_data[f] = objects_d[product.reference][f]
                if product_data:
                    if group.name not in group_data_d[level]:
                        group_data_d[level][group.name] = {}
                    group_data_d[level][group.name]['common'] = product_data

                ## calculem els atributs
                product_d = {}
                attributes = [self.get_efective_field_name(x.name) for x in group.attribute_ids]
                for child, data in childs.items():
                    # si es un grup o un producte final (leaf)
                    is_leaf = not data
                    product = child if is_leaf else data
                    product_data = {}
                    for a in attributes:
                        if a in objects_d[product.reference]:
                            product_data[a] = objects_d[product.reference][a]
                    label = product.reference if is_leaf else child.name
                    product_d[label] = product_data
                if product_d:
                    if group.name not in group_data_d[level]:
                        group_data_d[level][group.name] = {}
                    product_wrap_d = {
                        'group_level': None if is_leaf else child.level,
                        'data': product_d,
                    }
                    group_data_d[level][group.name]['attribute'] = product_wrap_d

        res.update({'groups': group_data_d})
        _logger.info("Group data successfully generated...")

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

                res.update({'families': family_ld})

            _logger.info("Family data successfully generated...")

            ## generm la informacio de les aplicacions
            _logger.info("Generating category data...")
            categories = objects.mapped('category_id')
            if categories:
                category_ld = []
                for category in categories.sorted(lambda x: x.sequence):
                    category_d = {
                        'id': category.id,
                    }
                    # adjunts ordenats
                    if category.attachment_ids:
                        attachments = category.attachment_ids \
                            .sorted(lambda x: (x.sequence, x.id))
                        if attachments:
                            category_d.update({
                                'attachment': {
                                    'datas_fname': attachments[0].datas_fname,
                                    'store_fname': attachments[0].attachment_id.store_fname,
                                },
                            })

                    name_lang_d = {}
                    for lang in active_langs:
                        lang_name = category.with_context(lang=lang).name
                        if lang_name:
                            name_lang_d[lang] = lang_name

                    if name_lang_d:
                        category_d.update({
                            'name': name_lang_d,
                        })
                        category_ld.append(category_d)

                res.update({'categories': category_ld})

            _logger.info("Category data successfully generated...")

        _logger.info("Generating product bundles...")

        finish_attribute = 'json_display_finish'
        group_d = {}
        for obj in objects:
            group_id = getattr(obj, 'product_group_id', None)
            if group_id:
                if group_id.attribute_ids.mapped('name') == [finish_attribute]:
                    if group_id not in group_d:
                        group_d[group_id] = []
                    group_d[group_id].append(obj)

        # generem els bundles agrupant cada bundle i posant dins tots els tempaltes
        # dels requireds associats
        bundle_d = {}
        for group_id, objects_l in group_d.items():
            products = self.env['lighting.product'].browse([x.id for x in objects_l])
            is_bundle_template = any(products.mapped('is_composite'))
            if is_bundle_template:
                group_d = {}
                # state
                group_d['enabled'] = any(products.mapped('website_published'))
                # required products
                domain = [('id', 'in', products.mapped('required_ids.id'))]
                if self.domain:
                    domain += ast.literal_eval(self.domain)
                products_required = self.env['lighting.product'].search(domain)
                if products_required:
                    ## components/accessories
                    accessory_l = []
                    for r in products_required:
                        if r.product_group_id and \
                                group_id.attribute_ids.mapped('name') == [finish_attribute]:
                            accessory_l.append({r.product_group_id.name: r.product_group_id.level})
                        else:
                            accessory_l.append({r.reference: None})
                    if accessory_l:
                        group_d['accessory'] = accessory_l

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
                        group_d['attachment'] = {
                            'datas_fname': attachment_ids[0].datas_fname,
                            'store_fname': attachment_ids[0].attachment_id.store_fname,
                        }
                if group_d:
                    bundle_d[group_id.name] = {
                        'group_level': group_id.level,
                        'data': group_d,
                    }

        res.update({'bundles': bundle_d})
        _logger.info("Product bundles generated.")

        _logger.info("Export data successfully done")

        return res
