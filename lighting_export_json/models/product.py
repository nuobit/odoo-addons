# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _

import re
import json


class LightingProduct(models.Model):
    _inherit = 'lighting.product'

    #### auxiliary function to get non db translations
    def _(self, string):
        return _(string)

    ######### Template #############################
    template = fields.Char(string='Template',
                           compute='_compute_template')

    @api.depends('reference',
                 )
    def _compute_template(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                m = re.match(r'^(.+)-.{2}$', rec.reference)
                if m:
                    template_reference = m.group(1)
                    template_reference_pattern = '%s-__' % template_reference
                    product_count = self.env['lighting.product'].search_count([
                        ('reference', '=like', template_reference_pattern),
                    ])
                    rec.template = template_reference if product_count > 1 else rec.reference

    ######### Display Cut hole dimensions ##########
    cut_hole_display = fields.Char(string='Cut hole',
                                   compute='_compute_cut_hole_display')

    @api.depends('recess_dimension_ids',
                 'recess_dimension_ids.type_id',
                 'recess_dimension_ids.value',
                 'recess_dimension_ids.sequence')
    def _compute_cut_hole_display(self):
        for prod in self:
            dims = prod.recess_dimension_ids
            if dims:
                same_uom = True
                uoms = set()
                for rec in dims:
                    if rec.type_id.uom not in uoms:
                        if not uoms:
                            uoms.add(rec.type_id.uom)
                        else:
                            same_uom = False
                            break

                res_label = ' x '.join(['%s' % x.type_id.name for x in dims])
                res_value = ' x '.join(['%g' % x.value for x in dims])

                if same_uom:
                    res_label = '%s (%s)' % (res_label, uoms.pop())
                else:
                    res_value = ' x '.join(['%g%s' % (x.value, x.type_id.uom) for x in dims])

                prod.recess_dimension_display = '%s: %s' % (res_label, res_value)

    ######### Attachments ##########
    attachment_display = fields.Serialized(string="Attachments",
                                           compute='_compute_attachment_display')

    @api.depends('attachment_ids.datas_fname',
                 'attachment_ids.sequence',
                 'attachment_ids.attachment_id.store_fname',
                 'attachment_ids.type_id.code',
                 'attachment_ids.type_id.name',
                 )
    def _compute_attachment_display(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                attachment_l = []
                for a in rec.attachment_ids.sorted(lambda x: x.sequence):
                    if a.type_id.id not in template_id.attachment_ids.mapped('type_id.id'):
                        continue

                    attachment_d = {
                        'datas_fname': a.datas_fname,
                        'store_fname': a.attachment_id.store_fname,
                    }

                    type_lang_d = {}
                    for lang in template_id.lang_ids.mapped('code'):
                        type_lang_d[lang] = a.with_context(lang=lang).type_id.display_name
                    if type_lang_d:
                        attachment_d.update({
                            'type_id': type_lang_d
                        })

                    if attachment_d:
                        attachment_l.append(attachment_d)

                if attachment_l:
                    rec.attachment_display = json.dumps(attachment_l)

    ######### Sources ##########
    source_display = fields.Serialized(string="Light sources",
                                       compute='_compute_source_display')

    @api.depends('source_ids.line_full_display',
                 'source_ids.sequence',
                 )
    def _compute_source_display(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                source_l = []
                for a in rec.source_ids.sorted(lambda x: x.sequence):
                    source_d = {
                        'sequence': a.sequence,
                    }

                    display_lang_d = {}
                    for lang in template_id.lang_ids.mapped('code'):
                        display_lang_d[lang] = a.with_context(lang=lang).line_full_display
                    if display_lang_d:
                        source_d.update({
                            'line_full_display': display_lang_d
                        })

                    if source_d:
                        source_l.append(source_d)

                if source_l:
                    rec.source_display = json.dumps(source_l)

    ######### Beams ##########
    beam_display = fields.Serialized(string="Light beams",
                                     compute='_compute_beam_display')

    @api.depends('beam_ids.line_full_display',
                 'beam_ids.sequence',
                 )
    def _compute_beam_display(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                beam_l = []
                for a in rec.beam_ids.sorted(lambda x: x.sequence):
                    beam_d = {
                        'sequence': a.sequence,
                    }

                    display_lang_d = {}
                    for lang in template_id.lang_ids.mapped('code'):
                        display_lang_d[lang] = a.with_context(lang=lang).line_full_display
                    if display_lang_d:
                        beam_d.update({
                            'line_full_display': display_lang_d
                        })

                    if beam_d:
                        beam_l.append(beam_d)

                if beam_l:
                    rec.beam_display = json.dumps(beam_l)

    ######### Template Accessories ##########
    template_accessory_display = fields.Serialized(string="Template accessories",
                                                   compute='_compute_template_accessory_display')

    @api.depends('accessory_ids')
    def _compute_template_accessory_display(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                if rec.accessory_ids:
                    template_accessory_published = rec.accessory_ids.filtered(lambda x: x.state == 'published')
                    template_accessory_l = list(set(template_accessory_published.mapped('template')))
                    rec.template_accessory_display = json.dumps(sorted(template_accessory_l))

    ######### Template Subtitutes ##########
    template_substitute_display = fields.Serialized(string="Template substitutes",
                                                    compute='_compute_template_substitute_display')

    @api.depends('substitute_ids')
    def _compute_template_substitute_display(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                if rec.substitute_ids:
                    template_substitute_published = rec.substitute_ids.filtered(lambda x: x.state == 'published')
                    template_substitute_l = list(set(template_substitute_published.mapped('template')))
                    rec.template_substitute_display = json.dumps(sorted(template_substitute_l))

    ######### Search Materials ##########
    search_material_ids = fields.Many2many(string="Search material",
                                           comodel_name='lighting.product.material',
                                           compute='_compute_search_material')

    @api.depends('body_material_ids',
                 'diffusor_material_ids',
                 'frame_material_ids',
                 'reflector_material_ids')
    def _compute_search_material(self):
        fields = [
            'body_material_ids', 'diffusor_material_ids',
            'frame_material_ids', 'reflector_material_ids',
            # 'blade_material_ids',
        ]
        for rec in self:
            materials_s = set()
            for field in fields:
                objs = getattr(rec, field)
                if objs:
                    materials_s |= set([x.id for x in objs])

            if materials_s:
                objs = self.env['lighting.product.material'].browse(list(materials_s))
                rec.search_material_ids = [(4, x.id, False) for x in objs.sorted(lambda x: x.display_name)]

    ######### Search CRI ##########
    search_cri = fields.Serialized(string="Search CRI",
                                   compute='_compute_search_cri')

    @api.depends('source_ids.line_ids.cri_min')
    def _compute_search_cri(self):
        for rec in self:
            cris = rec.source_ids.mapped('line_ids').filtered(
                lambda x: x.cri_min != 0 and x.is_led and
                          (x.is_integrated or x.is_lamp_included)).mapped('cri_min')

            rec.search_cri = json.dumps(sorted(list(set(cris))))

    ######### Search Beams ##########
    search_beam_angle = fields.Serialized(string="Search beam angle",
                                          compute='_compute_search_beam_angle')

    @api.depends('beam_ids.dimension_ids.value',
                 'beam_ids.dimension_ids.type_id',
                 'beam_ids.dimension_ids.type_id.name',
                 'beam_ids.dimension_ids.type_id.uom',
                 )
    def _compute_search_beam_angle(self):
        for rec in self:
            angles = rec.beam_ids.mapped('dimension_ids.value')
            rec.search_beam_angle = json.dumps(sorted(list(set(angles))))

    ######### Search Wattage ##########
    search_wattage = fields.Serialized(string="Search wattage",
                                       compute='_compute_search_wattage')

    @api.depends('source_ids.line_ids.wattage',
                 )
    def _compute_search_wattage(self):
        for rec in self:
            w_integrated = 0
            wattages_s = set()
            for line in rec.source_ids.mapped('line_ids'):
                if line.wattage:
                    wattage = line.wattage * line.source_id.num
                    if line.is_integrated:
                        w_integrated += wattage
                    else:
                        wattages_s.add(wattage)

            wattages_s2 = set()
            for w in wattages_s:
                wattages_s2.add(w + w_integrated)

            if wattages_s2:
                rec.search_wattage = json.dumps(sorted(list(wattages_s2)))

    ######### Search Color temperature ##########
    search_color_temperature = fields.Serialized(string="Search color temperature",
                                                 compute='_compute_search_color_temperature')

    @api.depends('source_ids.line_ids.color_temperature_id.value',
                 )
    def _compute_search_color_temperature(self):
        for rec in self:
            colork_s = set()
            for line in rec.source_ids.mapped('line_ids'):
                if line.is_integrated:
                    if line.color_temperature_id:
                        colork_s.add(line.color_temperature_id.value)

            if colork_s:
                rec.search_color_temperature = json.dumps(sorted(list(colork_s)))

    ######### Search Luminoux flux ##########
    search_luminous_flux = fields.Serialized(string="Search luminous flux",
                                             compute='_compute_search_luminous_flux')

    @api.depends('source_ids.line_ids.luminous_flux1',
                 'source_ids.line_ids.luminous_flux2',
                 )
    def _compute_search_luminous_flux(self):
        for rec in self:
            fluxes_s = set()
            for line in rec.source_ids.mapped('line_ids'):
                if line.is_integrated:
                    if line.luminous_flux1:
                        flux1 = line.luminous_flux1 * line.source_id.num
                        fluxes_s.add(flux1)
                    if line.luminous_flux2:
                        flux2 = line.luminous_flux2 * line.source_id.num
                        fluxes_s.add(flux2)

            if fluxes_s:
                rec.search_luminous_flux = json.dumps(sorted(list(fluxes_s)))

    ######### Search Source type flux ##########
    search_source_type = fields.Serialized(string="Search source type",
                                           compute='_compute_search_source_type')

    @api.depends('source_ids.line_ids.is_integrated',
                 'source_ids.line_ids.is_led',
                 )
    def _compute_search_source_type(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                leds_integrated = rec.source_ids.mapped('line_ids').filtered(lambda x: x.is_led and x.is_integrated)
                type_str = 'LED' if leds_integrated else 'Other'

                source_type_d = {}
                for lang in template_id.lang_ids.mapped('code'):
                    source_type_d[lang] = rec.with_context(lang=lang)._(type_str)

                if source_type_d:
                    rec.search_source_type = json.dumps(source_type_d)
