# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _

import datetime
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


def get_group_type(group, typ):
    if typ in group.mapped('type_ids.code'):
        return group
    else:
        if group.parent_id:
            return get_group_type(group.parent_id, typ)

    return None


class LightingProduct(models.Model):
    _inherit = 'lighting.product'

    #### auxiliary function to get non db translations
    def _(self, string):
        return _(string)

    ############### Auxiliar fields ###############################
    finish_group_name = fields.Char(string='Finish group name',
                                    compute='_compute_finish_group_name')

    def _compute_finish_group_name(self):
        for rec in self:
            if 'FINISH' in rec.product_group_id.type_ids.mapped('code'):
                rec.finish_group_name = rec.product_group_id.name
            else:
                rec.finish_group_name = rec.reference

    photo_group_id = fields.Many2one(comodel_name='lighting.product.group',
                                     string='Photo group',
                                     compute='_compute_foto_group')

    def _compute_foto_group(self):
        for rec in self:
            if rec.product_group_id:
                rec.photo_group_id = get_group_type(rec.product_group_id, 'PHOTO')

    group_description = fields.Char(string="Group description",
                                    compute="_compute_group_description")

    def _compute_group_description(self):
        for rec in self:
            description_l = filter(lambda x: x, [
                rec.category_id and rec.category_id.description_text or rec.category_id.name,
                rec.photo_group_id and rec.photo_group_id.alt_name or rec.photo_group_id.name,
            ])

            description = ' '.join(description_l)
            if description:
                rec.group_description = description

    ############### Display fields ################################

    json_display_finish_group_name = fields.Char(string='Finish group name JSON Display',
                                                 compute='_compute_json_display_finish_group_name')

    def _compute_json_display_finish_group_name(self):
        for rec in self:
            if rec.finish_group_name != rec.reference:
                rec.json_display_finish_group_name = rec.finish_group_name

    ## Display Finish
    json_display_finish = fields.Serialized(string='Finish JSON Display',
                                            compute='_compute_json_display_finish')

    @api.depends('finish_id',
                 'finish_id.code',
                 'finish_id.name',
                 'finish_id.html_color')
    def _compute_json_display_finish(self):
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
                        rec.json_display_finish = json.dumps(finish_d)

    ## Display Attachments
    json_display_attachment = fields.Serialized(string='Attachments JSON Display',
                                                compute='_compute_json_display_attachment')

    @api.depends('attachment_ids.datas_fname',
                 'attachment_ids.sequence',
                 'attachment_ids.attachment_id.store_fname',
                 'attachment_ids.type_id.code',
                 'attachment_ids.type_id.name',
                 )
    def _compute_json_display_attachment(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                # map attach type with order
                attachment_order_d = {x.type_id: x.sequence for x in template_id.attachment_ids}

                # classify
                attachment_type_d = {}
                for a in rec.attachment_ids:
                    attach_type = a.type_id
                    if attach_type in attachment_order_d:
                        if attach_type not in attachment_type_d:
                            attachment_type_d[attach_type] = self.env['lighting.attachment']
                        attachment_type_d[attach_type] |= a

                # final attachment sort and formatting
                if attachment_type_d:
                    attachment_l = []
                    for dummy, attachs in sorted(attachment_type_d.items(), key=lambda x: attachment_order_d[x[0]]):
                        a = attachs.filtered(lambda x: x.date)
                        if a:
                            a = a.sorted(lambda x: fields.Date.from_string(x.date), reverse=True)[0]
                        else:
                            a = attachs.sorted(lambda x: (x.sequence, x.id))[0]

                        attachment_d = {
                            'datas_fname': a.datas_fname,
                            'store_fname': a.attachment_id.store_fname,
                            'type': a.type_id.code,
                        }

                        type_lang_d = {}
                        for lang in template_id.lang_ids.mapped('code'):
                            type_lang_d[lang] = a.type_id.with_context(lang=lang).name
                        if type_lang_d:
                            attachment_d.update({
                                'label': type_lang_d,
                            })

                        attachment_l.append(attachment_d)

                    if attachment_l:
                        rec.json_display_attachment = json.dumps(attachment_l)

    ## Display Sources
    json_display_source_type = fields.Serialized(string="Source type JSON Display",
                                                 compute='_compute_json_display_source_type')

    @api.depends('source_ids.lampholder_id',
                 'source_ids.line_ids',
                 'source_ids.line_ids.type_id',
                 'source_ids.line_ids.type_id.name',
                 'source_ids.sequence')
    def _compute_json_display_source_type(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                rec.json_display_source_type = json.dumps(rec.source_ids.get_source_type())

    ## Display Color temperature
    json_display_color_temperature = fields.Serialized(string="Color temperature JSON Display",
                                                       compute='_compute_json_display_color_temperature')

    @api.depends('source_ids', 'source_ids.line_ids',
                 'source_ids.line_ids.color_temperature_id',
                 'source_ids.sequence')
    def _compute_json_display_color_temperature(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                rec.json_display_color_temperature = json.dumps(rec.source_ids.get_color_temperature())

    ## Display Luminous flux
    json_display_luminous_flux = fields.Serialized(string="Luminous flux JSON Display",
                                                   compute='_compute_json_display_luminous_flux')

    @api.depends('source_ids', 'source_ids.line_ids',
                 'source_ids.line_ids.luminous_flux1',
                 'source_ids.line_ids.luminous_flux2',
                 'source_ids.sequence')
    def _compute_json_display_luminous_flux(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                rec.json_display_luminous_flux = json.dumps(rec.source_ids.get_luminous_flux())

    ## Display Wattage
    json_display_wattage = fields.Serialized(string="Wattage JSON Display",
                                             compute='_compute_json_display_wattage')

    @api.depends('source_ids', 'source_ids.line_ids',
                 'source_ids.line_ids.wattage',
                 'source_ids.line_ids.wattage_magnitude',
                 'source_ids.sequence')
    def _compute_json_display_wattage(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                rec.json_display_wattage = json.dumps(rec.source_ids.get_wattage())

    ## Display Beams
    json_display_beam = fields.Serialized(string="Beam JSON Display",
                                          compute='_compute_json_display_beam')

    @api.depends('beam_ids.dimension_ids',
                 'beam_ids.dimension_ids.value',
                 'beam_ids.dimension_ids.type_id',
                 'beam_ids.dimension_ids.type_id.uom',
                 'beam_ids.photometric_distribution_ids',
                 'beam_ids.photometric_distribution_ids.name',
                 'beam_ids.sequence')
    def _compute_json_display_beam(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                for rec in self:
                    rec.json_display_beam = json.dumps(rec.beam_ids.get_beam())

    ## Display Beam Angle
    json_display_beam_angle = fields.Serialized(string="Beam angle JSON Display",
                                                compute='_compute_json_display_beam_angle')

    @api.depends('beam_ids.dimension_ids',
                 'beam_ids.dimension_ids.value',
                 'beam_ids.dimension_ids.type_id',
                 'beam_ids.dimension_ids.type_id.uom',
                 'beam_ids.sequence')
    def _compute_json_display_beam_angle(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                rec.json_display_beam_angle = json.dumps(rec.beam_ids.get_beam_angle())

    ## Display Cut hole dimension
    json_display_cut_hole_dimension = fields.Char(string='Cut hole dimension JSON Display',
                                                  compute='_compute_json_display_cut_hole_dimension')

    @api.depends('recess_dimension_ids',
                 'recess_dimension_ids.type_id',
                 'recess_dimension_ids.value',
                 'recess_dimension_ids.sequence')
    def _compute_json_display_cut_hole_dimension(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                rec.json_display_cut_hole_dimension = rec.recess_dimension_ids.get_display()

    ## Display Dimension
    json_display_dimension = fields.Char(string='Dimension JSON Display',
                                         compute='_compute_json_display_dimension')

    @api.depends('dimension_ids',
                 'dimension_ids.type_id',
                 'dimension_ids.value',
                 'dimension_ids.sequence')
    def _compute_json_display_dimension(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                rec.json_display_dimension = rec.dimension_ids.get_display()

    ## Display Optional products
    json_display_optional = fields.Serialized(string="Optional JSON Display",
                                              compute='_compute_json_display_optional')

    @api.depends('optional_ids')
    def _compute_json_display_optional(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                if rec.optional_ids:
                    template_optional_published = rec.optional_ids.filtered(lambda x: x.state == 'published')
                    template_optional_l = list(set(template_optional_published.mapped('finish_group_name')))
                    if template_optional_l:
                        rec.json_display_optional = json.dumps(sorted(template_optional_l))

    ## Display Subtitutes
    json_display_substitute = fields.Serialized(string="Substitute JSON Display",
                                                compute='_compute_json_display_substitute')

    @api.depends('substitute_ids')
    def _compute_json_display_substitute(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                if rec.substitute_ids:
                    template_substitute_published = rec.substitute_ids.filtered(lambda x: x.state == 'published')
                    template_substitute_l = list(set(template_substitute_published.mapped('finish_group_name')))
                    rec.json_display_substitute = json.dumps(sorted(template_substitute_l))

    ## Display First Product Photo
    json_display_photo = fields.Serialized(string="Photo JSON Display",
                                           compute='_compute_json_display_photo')

    def _compute_json_display_photo(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            attachment_order_d = {x.type_id: x.sequence for x in template_id.attachment_ids}
            for rec in self:
                if rec.product_group_id:
                    attachment_ids = rec.product_group_id.flat_product_ids.mapped('attachment_ids')
                else:
                    attachment_ids = rec.attachment_ids

                images = attachment_ids.filtered(lambda x: x.type_id.is_image and
                                                           x.type_id in attachment_order_d.keys())
                if images:
                    images = images.sorted(lambda x: (attachment_order_d[x.type_id],
                                                      x.product_id.sequence, x.sequence, x.id))
                    attachment_d = {
                        'datas_fname': images[0].datas_fname,
                        'store_fname': images[0].attachment_id.store_fname,
                    }
                    rec.json_display_photo = json.dumps(attachment_d)

    ##################### Search fields ##################################

    ## Search Materials
    json_search_material_ids = fields.Many2many(string="Material JSON Search",
                                                comodel_name='lighting.product.material',
                                                compute='_compute_json_search_material_ids')

    @api.depends('body_material_ids')
    def _compute_json_search_material_ids(self):
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
                rec.json_search_material_ids = [(4, x.id, False) for x in objs.sorted(lambda x: x.display_name)]

    ## Search CRI
    json_search_cri = fields.Serialized(string="CRI JSON Search",
                                        compute='_compute_json_search_cri')

    @api.depends('source_ids.line_ids.cri_min')
    def _compute_json_search_cri(self):
        for rec in self:
            cris = rec.source_ids.mapped('line_ids').filtered(
                lambda x: x.cri_min != 0 and x.is_led and
                          (x.is_integrated or x.is_lamp_included)).mapped('cri_min')

            rec.json_search_cri = json.dumps(sorted(list(set(cris))))

    ## Search Beam
    json_search_beam_angle = fields.Serialized(string="Beam angle JSON Search",
                                               compute='_compute_json_search_beam_angle')

    @api.depends('beam_ids.dimension_ids.value',
                 'beam_ids.dimension_ids.type_id',
                 'beam_ids.dimension_ids.type_id.name',
                 'beam_ids.dimension_ids.type_id.uom',
                 )
    def _compute_json_search_beam_angle(self):
        for rec in self:
            angles = rec.beam_ids.mapped('dimension_ids.value')
            if angles:
                arange = [(0, 20), (20, 40), (40, 60),
                          (60, 80), (80, 100), (100, float('inf'))]
                a_ranges = _values2range(angles, arange, magnitude='\u00B0')
                if a_ranges:
                    rec.json_search_beam_angle = json.dumps(a_ranges)

    ## Search Wattage
    json_search_wattage = fields.Serialized(string="Wattage JSON Search",
                                            compute='_compute_json_search_wattage')

    @api.depends('source_ids.line_ids.wattage',
                 )
    def _compute_json_search_wattage(self):
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
                    rec.json_search_wattage = json.dumps(wattage_ranges)

    ## Search Color temperature
    json_search_color_temperature = fields.Serialized(string="Color temperature JSON Search",
                                                      compute='_compute_json_search_color_temperature')

    @api.depends('source_ids.line_ids.color_temperature_id.value',
                 )
    def _compute_json_search_color_temperature(self):
        for rec in self:
            colork_s = set()
            for line in rec.source_ids.mapped('line_ids'):
                if line.is_integrated:
                    if line.color_temperature_id:
                        colork_s.add(line.color_temperature_id.value)

            if colork_s:
                krange = [(0, 3000), (3000, 3500), (3500, 4000),
                          (4000, 5000), (5000, float('inf'))]
                k_ranges = _values2range(colork_s, krange, magnitude='K')
                if k_ranges:
                    rec.json_search_color_temperature = json.dumps(k_ranges)

    ## Search Luminoux flux
    json_search_luminous_flux = fields.Serialized(string="Luminous flux JSON Search",
                                                  compute='_compute_json_search_luminous_flux')

    @api.depends('source_ids.line_ids.luminous_flux1',
                 'source_ids.line_ids.luminous_flux2',
                 )
    def _compute_json_search_luminous_flux(self):
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
                    rec.json_search_luminous_flux = json.dumps(flux_ranges)

    ## Search Source type flux
    json_search_source_type = fields.Serialized(string="Source type JSON Search",
                                                compute='_compute_json_search_source_type')

    @api.depends('source_ids.line_ids.is_integrated',
                 'source_ids.line_ids.is_led',
                 )
    def _compute_json_search_source_type(self):
        template_id = self.env.context.get('template_id')
        if template_id:
            for rec in self:
                leds_integrated = rec.source_ids.mapped('line_ids').filtered(lambda x: x.is_led and x.is_integrated)
                type_str = 'LED' if leds_integrated else 'Other'

                source_type_d = {}
                for lang in template_id.lang_ids.mapped('code'):
                    source_type_d[lang] = rec.with_context(lang=lang)._(type_str)

                if source_type_d:
                    rec.json_search_source_type = json.dumps(source_type_d)
