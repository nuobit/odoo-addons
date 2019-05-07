# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _

import re
import json


def _values2range(values, range, magnitude=None):
    ranges = []
    for w in values:
        for r in range:
            min, max = r
            if min <= w and w < max:
                if r not in ranges:
                    ranges.append(r)
                    break

    ranges_str = []
    for min, max in sorted(ranges):
        if min != float('-inf') and max != float('inf'):
            range = "%i - %i" % (min, max)
        elif min != float('-inf') and max == float('inf'):
            range = "> %i" % min
        elif min == float('-inf') and max != float('inf'):
            range = "< %i" % max
        else:
            range = '-\u221E - \u221E'

        if magnitude:
            range = "%s%s" % (range, magnitude)

        ranges_str.append(range)

    return ranges_str


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
        for rec in self:
            m = re.match(r'^(.+)-.{2}$', rec.reference)
            if m:
                template_reference = m.group(1)
                template_reference_pattern = '%s-__' % template_reference
                product_count = self.env['lighting.product'].search_count([
                    ('reference', '=like', template_reference_pattern),
                ])
                rec.template = template_reference if product_count > 1 else rec.reference

    template_display = fields.Char(string='Template',
                                   compute='_compute_template_display')

    def _compute_template_display(self):
        for rec in self:
            if rec.template != rec.reference:
                rec.template_display = rec.template

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

    ######### Finish ##########
    finish_display = fields.Serialized(string='Finish',
                                       compute='_compute_finish_display')

    @api.depends('finish_id',
                 'finish_id.code',
                 'finish_id.name',
                 'finish_id.html_color')
    def _compute_finish_display(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                if rec.finish_id:
                    finish_d = {}
                    finish_lang_d = {}
                    for lang in template_id.lang_ids.mapped('code'):
                        finish_lang_d[lang] = rec.finish_id.with_context(lang=lang).name
                    if finish_lang_d:
                        finish_d.update({
                            'description': finish_lang_d
                        })
                    if rec.finish_id.html_color:
                        finish_d.update({
                            'html_color': rec.finish_id.html_color
                        })

                    if finish_d:
                        rec.finish_display = json.dumps(finish_d)

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
                n = template_id.max_attachments
                if n < 0:
                    n = len(rec.attachment_ids)

                attachment_ids = set()
                while n > 0:
                    base_count = {x.type_id.id: x.max_count for x in
                                  template_id.attachment_ids.filtered(lambda x: x.max_count != 0)}
                    attachments = rec.attachment_ids \
                        .filtered(lambda x: x.id not in attachment_ids and
                                            x.type_id.id in base_count) \
                        .sorted(lambda x: x.sequence)
                    if not attachments:
                        break
                    for a in attachments:
                        if a.type_id.id in base_count:
                            max_count = base_count[a.type_id.id]
                            if max_count != 0:
                                attachment_ids.add(a.id)
                                if max_count > 0:
                                    base_count[a.type_id.id] -= 1
                                n -= 1
                                if not n:
                                    break

                if attachment_ids:
                    attachment_l = []
                    for a in rec.attachment_ids \
                            .filtered(lambda x: x.id in attachment_ids) \
                            .sorted(lambda x: x.sequence):
                        attachment_l.append({
                            'datas_fname': a.datas_fname,
                            'store_fname': a.attachment_id.store_fname,
                            'type': a.type_id.code,
                        })

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

    ######### Template Optional ##########
    template_optional_display = fields.Serialized(string="Template optional",
                                                  compute='_compute_template_optional_display')

    @api.depends('optional_ids')
    def _compute_template_optional_display(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                if rec.optional_ids:
                    template_optional_published = rec.optional_ids.filtered(lambda x: x.state == 'published')
                    template_optional_l = list(set(template_optional_published.mapped('template')))
                    if template_optional_l:
                        rec.template_optional_display = json.dumps(sorted(template_optional_l))

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

    @api.depends('body_material_ids')
    def _compute_search_material(self):
        fields = [
            'body_material_ids'
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
            if angles:
                arange = [(0, 20), (20, 40), (40, 60),
                          (60, 80), (80, 100), (100, float('inf'))]
                a_ranges = _values2range(angles, arange, magnitude='\u00B0')
                if a_ranges:
                    rec.search_beam_angle = json.dumps(a_ranges)

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
                wrange = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, float('inf'))]
                wattage_ranges = _values2range(wattages_s2, wrange, magnitude='W')
                if wattage_ranges:
                    rec.search_wattage = json.dumps(wattage_ranges)

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
                krange = [(float('-inf'), 3000), (3000, 3500), (3500, 4000),
                          (4000, 5000), (5000, float('inf'))]
                k_ranges = _values2range(colork_s, krange, magnitude='K')
                if k_ranges:
                    rec.search_color_temperature = json.dumps(k_ranges)

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
                fxrange = [(0, 400), (400, 800), (800, 1200),
                           (1200, 1600), (1600, 2000), (2000, float('inf'))]
                flux_ranges = _values2range(fluxes_s, fxrange, magnitude='Lm')
                if flux_ranges:
                    rec.search_luminous_flux = json.dumps(flux_ranges)

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

    #################### backwards compatibility fields
    ### they should be replaced by the actual field on lighting.product object

    ######### category_ids (many2many) (former application_ids), should be used category_id (many2one)
    # directly on the template instead and remove this completely
    category_ids = fields.Many2many(string="Categories",
                                    compute='_compute_product_categories')

    @api.depends('category_id')
    def _compute_product_categories(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                if rec.category_id:
                    rec.category_ids = [(6, False, [rec.category_id.id])]
