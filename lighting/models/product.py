# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import re
from collections import OrderedDict

YESNO = [
    ('Y', _('Yes')),
    ('N', _('No')),
]


class LightingProduct(models.Model):
    _name = 'lighting.product'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'reference'
    _order = 'sequence,reference'
    _description = 'Product'

    # Common data
    reference = fields.Char(string='Reference', required=True, track_visibility='onchange')

    # image: all image fields are base64 encoded and PIL-supported
    image_small = fields.Binary("Small-sized image", attachment=True, compute='_compute_images', store=True)
    image_medium = fields.Binary("Medium-sized image", attachment=True, compute='_compute_images', store=True)

    @api.depends('attachment_ids.datas', 'attachment_ids.image_small', 'attachment_ids.image_medium',
                 'attachment_ids.sequence',
                 'attachment_ids.type_id', 'attachment_ids.type_id.is_image')
    def _compute_images(self):
        for rec in self:
            resized_images = rec.attachment_ids.get_main_resized_images()
            if resized_images:
                rec.image_medium = resized_images['image_medium']
                rec.image_small = resized_images['image_small']

    description = fields.Char(compute='_compute_description', string='Description', readonly=True,
                              help="Description dynamically generated from product data",
                              translate=True, store=True, track_visibility='onchange')

    @api.depends('category_id.name',
                 'category_id.description_text',
                 'family_ids.name',
                 'catalog_ids.description_show_ip',
                 'sealing_id.name', 'sealing2_id.name',
                 'dimmable_ids.name',
                 'source_ids.sequence',
                 'source_ids.lampholder_id.code',
                 'source_ids.line_ids.sequence',
                 'source_ids.line_ids.type_id.code',
                 'source_ids.line_ids.type_id.is_integrated',
                 'source_ids.line_ids.type_id.description_text',
                 'source_ids.line_ids.is_lamp_included',
                 'source_ids.line_ids.wattage',
                 'source_ids.line_ids.wattage_magnitude',
                 'source_ids.line_ids.luminous_flux1',
                 'source_ids.line_ids.luminous_flux2',
                 'source_ids.line_ids.color_temperature_id.value',
                 'finish_id.name')
    def _compute_description(self):
        for rec in self:
            rec.description = rec._generate_description()

    def _generate_description(self, show_variant_data=True):
        self.ensure_one()
        data = []
        if self.category_id:
            data.append(self.category_id.description_text or self.category_id.name)

        if self.family_ids:
            data.append(','.join(self.family_ids.sorted(lambda x: x.sequence).mapped('name')))

        if self.catalog_ids:
            ip_catalogs = self.catalog_ids.filtered(lambda x: x.description_show_ip)
            if ip_catalogs:
                data_sealing = []
                for ipx in ('sealing_id', 'sealing2_id'):
                    sealing = getattr(self, ipx)
                    if sealing:
                        data_sealing.append(sealing.name)
                if data_sealing:
                    data.append(','.join(data_sealing))

        if self.dimmable_ids:
            data.append(','.join(self.dimmable_ids.sorted(lambda x: x.name).mapped('name')))

        data_sources = []
        for source in self.source_ids.sorted(lambda x: x.sequence):
            data_source = []
            if source.lampholder_id:
                data_source.append(source.lampholder_id.code)

            type_d = OrderedDict()
            for line in source.line_ids.sorted(lambda x: (x.type_id.is_integrated, x.sequence)):
                is_integrated = line.type_id.is_integrated
                if is_integrated not in type_d:
                    type_d[is_integrated] = []
                type_d[is_integrated].append(line)

            data_lines = []
            for is_integrated, lines in type_d.items():
                if is_integrated:
                    for line in lines:
                        data_line = []
                        data_line.append(line.type_id.description_text or line.type_id.code)

                        wattage_total_display = line.prepare_wattage_str(mult=line.source_id.num or 1,
                                                                         is_max_wattage=False)
                        if wattage_total_display:
                            data_line.append(wattage_total_display)

                        data_lm = []
                        for lmx in ('luminous_flux1', 'luminous_flux2'):
                            lm = getattr(line, lmx)
                            if lm:
                                data_lm.append('%i' % lm)
                        if data_lm != []:
                            lm_str = '%sLm' % '-'.join(data_lm)
                            if (line.source_id.num or 1) > 1:
                                lm_str = '%ix%s' % (line.source_id.num, lm_str)
                            data_line.append(lm_str)

                        if line.color_temperature_id:
                            data_line.append('%iK' % line.color_temperature_id.value)

                        if data_line:
                            data_lines.append(' '.join(data_line))
                else:
                    lamp_d = OrderedDict()
                    for line in lines:
                        is_lamp_included = line.is_lamp_included
                        if is_lamp_included not in lamp_d:
                            lamp_d[is_lamp_included] = []
                        lamp_d[is_lamp_included].append(line)

                    data_lines = []
                    for is_lamp_included, llines in lamp_d.items():
                        if is_lamp_included:
                            for line in llines:
                                data_line = []
                                data_line.append(line.type_id.description_text or line.type_id.code)

                                wattage_total_display = line.prepare_wattage_str(mult=line.source_id.num or 1,
                                                                                 is_max_wattage=False)
                                if wattage_total_display:
                                    data_line.append(wattage_total_display)

                                data_lm = []
                                for lmx in ('luminous_flux1', 'luminous_flux2'):
                                    lm = getattr(line, lmx)
                                    if lm:
                                        data_lm.append('%i' % lm)
                                if data_lm != []:
                                    lm_str = '%sLm' % '-'.join(data_lm)
                                    if (line.source_id.num or 1) > 1:
                                        lm_str = '%ix%s' % (line.source_id.num, lm_str)
                                    data_line.append(lm_str)

                                if line.color_temperature_id:
                                    data_line.append('%iK' % line.color_temperature_id.value)

                                if data_line:
                                    data_lines.append(' '.join(data_line))
                        else:
                            wattage_d = {}
                            for line in llines:
                                if line.wattage > 0 and line.wattage_magnitude:
                                    if line.wattage_magnitude not in wattage_d:
                                        wattage_d[line.wattage_magnitude] = []
                                    wattage_d[line.wattage_magnitude].append(line)

                            for wlines in wattage_d.values():
                                line_max = sorted(wlines, key=lambda x: x.wattage, reverse=True)[0]
                                wattage_total_display = line_max.prepare_wattage_str(mult=line_max.source_id.num or 1,
                                                                                     is_max_wattage=False)
                                if wattage_total_display:
                                    data_lines.append(wattage_total_display)

            if data_lines:
                data_source.append(','.join(data_lines))

            if data_source:
                data_sources.append(' '.join(data_source))

        if data_sources:
            data.append('+'.join(data_sources))

        if show_variant_data and self.finish_id:
            data.append(self.finish_id.name)

        if data:
            return ' '.join(data)
        else:
            return None

    description_manual = fields.Char(string='Description (manual)', help='Manual description', translate=True,
                                     track_visibility='onchange')

    ean = fields.Char(string='EAN', required=False, track_visibility='onchange')

    product_group_id = fields.Many2one(comodel_name='lighting.product.group',
                                       string='Group',
                                       ondelete='restrict', track_visibility='onchange')

    family_ids = fields.Many2many(comodel_name='lighting.product.family',
                                  relation='lighting_product_family_rel', string='Families',
                                  track_visibility='onchange')
    catalog_ids = fields.Many2many(comodel_name='lighting.catalog', relation='lighting_product_catalog_rel',
                                   string='Catalogs', required=True, track_visibility='onchange')

    category_id = fields.Many2one(comodel_name='lighting.product.category',
                                  string='Category', required=True,
                                  ondelete='restrict', track_visibility='onchange')

    category_completename = fields.Char(string='Category (complete name)',
                                         store=False,
                                         inverse='_inverse_category_complete_name')

    def _inverse_category_complete_name(self):
        for rec in self:
            if rec.category_completename:
                category_leafs = self.env['lighting.product.category']. \
                    get_leaf_from_complete_name(rec.category_completename)
                if category_leafs:
                    rec.category_id = category_leafs[0]
                else:
                    raise ValidationError(
                        _("Category with complete name '%s' does not exist") % rec.category_completename)
            else:
                rec.category_id = False

    is_composite = fields.Boolean(string="Is composite", default=False)

    @api.onchange('is_composite')
    def _onchange_is_composite(self):
        if not self.is_composite and self.required_ids:
            self.is_composite = True
            return {
                'warning': {'title': "Warning",
                            'message': _(
                                "You cannot change this while the product has necessary accessories assigned")},
            }

    parents_brand_ids = fields.Many2many(comodel_name='lighting.catalog',
                                         compute='_compute_parents_brands',
                                         readonly=True,
                                         string='Parents brands',
                                         help='Brands of the products that one of their optional and/or '
                                              'required accessories is the current product')

    @api.depends('optional_ids', 'required_ids')
    def _compute_parents_brands(self):
        for rec in self:
            parents = self.env['lighting.product'].search([
                '|',
                ('optional_ids', '=', rec.id),
                ('required_ids', '=', rec.id),
            ])
            if parents:
                brand_ids = list(set(parents.mapped('catalog_ids.id')))
                rec.parents_brand_ids = [(6, False, brand_ids)]

    last_update = fields.Date(string='Last modified on', track_visibility='onchange')

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order",
                              track_visibility='onchange')

    _sql_constraints = [('reference_uniq', 'unique (reference)', 'The reference must be unique!'),
                        ('ean_uniq', 'unique (ean)', 'The EAN must be unique!')
                        ]

    # Description tab
    location_ids = fields.Many2many(comodel_name='lighting.product.location',
                                    relation='lighting_product_location_rel', string='Locations',
                                    required=True,
                                    track_visibility='onchange')

    installation_ids = fields.Many2many(comodel_name='lighting.product.installation',
                                        relation='lighting_product_installation_rel', string='Installations',
                                        track_visibility='onchange')

    application_ids = fields.Many2many(comodel_name='lighting.product.application',
                                       relation='lighting_product_application_rel', string='Applications',
                                       track_visibility='onchange')
    finish_id = fields.Many2one(comodel_name='lighting.product.finish', ondelete='restrict', string='Finish',
                                track_visibility='onchange')

    finish_prefix = fields.Char(string='Finish prefix', compute='_compute_finish_prefix')

    def _compute_finish_prefix(self):
        for rec in self:
            has_sibling = False
            m = re.match(r'^(.+)-.{2}$', rec.reference)
            if m:
                prefix = m.group(1)
                product_siblings = self.search([
                    ('reference', '=like', '%s-__' % prefix),
                    ('id', '!=', rec.id),
                ])
                for p in product_siblings:
                    rec.finish_prefix = prefix
                    has_sibling = True
                    break

            if not has_sibling:
                rec.finish_prefix = rec.reference

    body_material_ids = fields.Many2many(comodel_name='lighting.product.material',
                                         relation='lighting_product_body_material_rel',
                                         string='Body material', track_visibility='onchange')
    diffusor_material_ids = fields.Many2many(comodel_name='lighting.product.material',
                                             relation='lighting_product_diffusor_material_rel',
                                             string='Diffuser material', track_visibility='onchange')
    frame_material_ids = fields.Many2many(comodel_name='lighting.product.material',
                                          relation='lighting_product_frame_material_rel',
                                          string='Frame material', track_visibility='onchange')
    reflector_material_ids = fields.Many2many(comodel_name='lighting.product.material',
                                              relation='lighting_product_reflector_material_rel',
                                              string='Reflector material', track_visibility='onchange')
    blade_material_ids = fields.Many2many(comodel_name='lighting.product.material',
                                          relation='lighting_product_blade_material_rel',
                                          string='Blade material', track_visibility='onchange')

    sealing_id = fields.Many2one(comodel_name='lighting.product.sealing',
                                 ondelete='restrict',
                                 string='Sealing', track_visibility='onchange')
    sealing2_id = fields.Many2one(comodel_name='lighting.product.sealing',
                                  ondelete='restrict',
                                  string='Sealing 2', track_visibility='onchange')

    ik = fields.Selection(selection=[("%02d" % x, "%02d" % x) for x in range(11)],
                          string='IK', track_visibility='onchange')

    static_pressure = fields.Float(string="Static pressure (kg)", track_visibility='onchange')
    dynamic_pressure = fields.Float(string="Dynamic pressure (kg)", track_visibility='onchange')
    dynamic_pressure_velocity = fields.Float(string="Dynamic pressure (km/h)", track_visibility='onchange')
    corrosion_resistance = fields.Selection(selection=YESNO, string="Corrosion resistance", track_visibility='onchange')
    technical_comments = fields.Char(string='Technical comments', track_visibility='onchange')

    # electrical characteristics tab
    protection_class_id = fields.Many2one(comodel_name='lighting.product.protectionclass',
                                          ondelete='restrict',
                                          string='Protection class', track_visibility='onchange')
    frequency_id = fields.Many2one(comodel_name='lighting.product.frequency',
                                   ondelete='restrict', string='Frequency (Hz)', track_visibility='onchange')
    dimmable_ids = fields.Many2many(comodel_name='lighting.product.dimmable',
                                    relation='lighting_product_dimmable_rel',
                                    string='Dimmables', track_visibility='onchange')
    auxiliary_equipment_ids = fields.Many2many(comodel_name='lighting.product.auxiliaryequipment',
                                               relation='lighting_product_auxiliary_equipment_rel',
                                               string='Auxiliary gear', track_visibility='onchange')
    auxiliary_equipment_model_ids = fields.One2many(comodel_name='lighting.product.auxiliaryequipmentmodel',
                                                    inverse_name='product_id',
                                                    string='Auxiliary gear code', copy=True,
                                                    track_visibility='onchange')
    auxiliary_equipment_model_alt = fields.Char(string='Alternative auxiliary gear code', track_visibility='onchange')
    input_voltage_id = fields.Many2one(comodel_name='lighting.product.voltage',
                                       ondelete='restrict', string='Input voltage', track_visibility='onchange')
    input_current = fields.Float(string='Input current (mA)', track_visibility='onchange')
    output_voltage_id = fields.Many2one(comodel_name='lighting.product.voltage',
                                        ondelete='restrict', string='Output voltage', track_visibility='onchange')
    output_current = fields.Float(string='Output current (mA)', track_visibility='onchange')

    total_wattage = fields.Float(compute='_compute_total_wattage',
                                 inverse='_inverse_total_wattage',
                                 string='Total wattage (W)', help='Total power consumed by the luminaire',
                                 store=True, track_visibility='onchange')
    total_wattage_auto = fields.Boolean(string='Autocalculate',
                                        help='Autocalculate total wattage', default=True, track_visibility='onchange')

    @api.depends('total_wattage_auto', 'source_ids.line_ids.wattage', 'source_ids.line_ids.type_id',
                 'source_ids.line_ids.type_id.is_integrated',
                 'source_ids.line_ids.is_lamp_included')
    def _compute_total_wattage(self):
        for rec in self:
            if rec.total_wattage_auto:
                rec.total_wattage = 0
                line_l = rec.source_ids.mapped('line_ids').filtered(lambda x: x.is_integrated or x.is_lamp_included)
                for line in line_l:
                    if line.wattage <= 0:
                        raise ValidationError("%s: The source line %s has invalid wattage" % (rec.display_name,
                                                                                              line.type_id.display_name))
                    rec.total_wattage += line.source_id.num * line.wattage

    def _inverse_total_wattage(self):
        ## dummy method. It allows to update calculated field
        pass

    power_factor_min = fields.Float(string='Minimum power factor', track_visibility='onchange')
    power_switches = fields.Integer(string='Power switches', help="Number of power switches",
                                    track_visibility='onchange')

    usb_ports = fields.Integer(string='USB ports', help="Number of USB ports", track_visibility='onchange')
    usb_voltage = fields.Float(string='USB voltage', track_visibility='onchange')
    usb_current = fields.Float(string='USB current', track_visibility='onchange')

    sensor_ids = fields.Many2many(comodel_name='lighting.product.sensor', relation='lighting_product_sensor_rel',
                                  string='Sensors', track_visibility='onchange')

    battery_autonomy = fields.Float(string='Battery autonomy (h)', track_visibility='onchange')
    battery_charge_time = fields.Float(string='Battery charge time (h)', track_visibility='onchange')
    surface_temperature = fields.Float(string='Surface temperature (ºC)', track_visibility='onchange')
    operating_temperature_min = fields.Float(string='Minimum operating temperature (ºC)', track_visibility='onchange')
    operating_temperature_max = fields.Float(string='Maximum operating temperature (ºC)', track_visibility='onchange')

    glow_wire_temperature = fields.Float(string='Glow wire temperature (ºC)', track_visibility='onchange')

    # light characteristics tab
    total_nominal_flux = fields.Float(string='Total flux (Lm)', help='Luminaire total nominal flux',
                                      track_visibility='onchange')
    ugr_max = fields.Integer(string='UGR', help='Maximum unified glare rating', track_visibility='onchange')

    lifetime = fields.Integer(string='Lifetime (h)', track_visibility='onchange')

    led_lifetime_l = fields.Integer(string='LED lifetime L', track_visibility='onchange')
    led_lifetime_b = fields.Integer(string='LED lifetime B', track_visibility='onchange')

    # Physical characteristics
    weight = fields.Float(string='Weight (kg)', track_visibility='onchange')
    dimension_ids = fields.One2many(comodel_name='lighting.product.dimension',
                                    inverse_name='product_id', string='Dimensions', copy=True,
                                    track_visibility='onchange')

    cable_outlets = fields.Integer(string='Cable outlets', help="Number of cable outlets", track_visibility='onchange')
    lead_wires = fields.Integer(string='Lead wires supplied', help="Number of lead wires supplied",
                                track_visibility='onchange')
    lead_wire_length = fields.Float(string='Length of the lead wire supplied (mm)', track_visibility='onchange')
    inclination_angle_max = fields.Float(string='Maximum tilt angle (º)', track_visibility='onchange')
    rotation_angle_max = fields.Float(string='Maximum rotation angle (º)', track_visibility='onchange')
    recessing_box_included = fields.Selection(selection=YESNO, string='Cut hole box included',
                                              track_visibility='onchange')
    recess_dimension_ids = fields.One2many(comodel_name='lighting.product.recessdimension',
                                           inverse_name='product_id', string='Cut hole dimensions',
                                           copy=True, track_visibility='onchange')
    ecorrae_category_id = fields.Many2one(comodel_name='lighting.product.ecorraecategory', ondelete='restrict',
                                          string='ECORRAE I category', track_visibility='onchange')
    ecorrae2_category_id = fields.Many2one(comodel_name='lighting.product.ecorraecategory', ondelete='restrict',
                                           string='ECORRAE II category', track_visibility='onchange')
    ecorrae = fields.Float(string='ECORRAE I', track_visibility='onchange')
    ecorrae2 = fields.Float(string='ECORRAE II', track_visibility='onchange')

    periodic_maintenance = fields.Selection(selection=YESNO, string='Periodic maintenance', track_visibility='onchange')
    anchorage_included = fields.Selection(selection=YESNO, string='Anchorage included', track_visibility='onchange')
    post_included = fields.Selection(selection=YESNO, string='Post included', track_visibility='onchange')
    post_with_inspection_chamber = fields.Selection(selection=YESNO, string='Post with inspection chamber',
                                                    track_visibility='onchange')

    emergency_light = fields.Selection(selection=YESNO, string='Emergency light', help="Luminarie with emergency light",
                                       track_visibility='onchange')
    average_emergency_time = fields.Float(string='Average emergency time (h)', track_visibility='onchange')

    flammable_surfaces = fields.Selection(selection=YESNO, string='Flammable surfaces', track_visibility='onchange')

    photobiological_risk_group_id = fields.Many2one(comodel_name='lighting.product.photobiologicalriskgroup',
                                                    ondelete='restrict',
                                                    string='Photobiological risk group', track_visibility='onchange')

    mechanical_screwdriver = fields.Selection(selection=YESNO, string='Electric screwdriver',
                                              track_visibility='onchange')

    fan_blades = fields.Integer(string='Fan blades', help='Number of fan blades', track_visibility='onchange')
    fan_control = fields.Selection(selection=[('remote', 'Remote control'), ('wall', 'Wall control')],
                                   string='Fan control type', track_visibility='onchange')
    fan_wattage_ids = fields.One2many(comodel_name='lighting.product.fanwattage',
                                      inverse_name='product_id', string='Fan wattages (W)', copy=True,
                                      track_visibility='onchange')

    # Sources tab
    source_ids = fields.One2many(comodel_name='lighting.product.source',
                                 inverse_name='product_id', string='Sources', copy=True, track_visibility='onchange')

    source_count = fields.Integer(compute='_compute_source_count', string='Total sources')

    @api.depends('source_ids')
    def _compute_source_count(self):
        for rec in self:
            rec.source_count = sum(rec.source_ids.mapped('num'))

    # Beams tab
    beam_ids = fields.One2many(comodel_name='lighting.product.beam',
                               inverse_name='product_id', string='Beams', copy=True, track_visibility='onchange')

    beam_count = fields.Integer(compute='_compute_beam_count', string='Total beams')

    @api.depends('beam_ids')
    def _compute_beam_count(self):
        for rec in self:
            rec.beam_count = sum(rec.beam_ids.mapped('num'))

    # Attachment tab
    attachment_ids = fields.One2many(comodel_name='lighting.attachment',
                                     inverse_name='product_id', string='Attachments', copy=True,
                                     track_visibility='onchange')
    attachment_count = fields.Integer(compute='_compute_attachment_count', string='Attachment(s)')

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = self.env['lighting.attachment'].search_count([('product_id', '=', record.id)])

    # Optional accesories tab
    optional_ids = fields.Many2many(comodel_name='lighting.product', relation='lighting_product_optional_rel',
                                    column1="product_id", column2='optional_id',
                                    string='Recommended accessories', track_visibility='onchange')

    parent_optional_accessory_product_count = fields.Integer(compute='_compute_parent_optional_accessory_product_count')

    @api.depends('optional_ids')
    def _compute_parent_optional_accessory_product_count(self):
        for record in self:
            record.parent_optional_accessory_product_count = self.env['lighting.product'] \
                .search_count([('optional_ids', '=', record.id)])

    is_optional_accessory = fields.Boolean(string='Is recommended accessory',
                                           compute='_compute_is_optional_accessory',
                                           search='_search_is_optional_accessory')

    @api.depends('optional_ids')
    def _compute_is_optional_accessory(self):
        for rec in self:
            parent_ids = self.env['lighting.product'].search([('optional_ids', '=', rec.id)])
            if parent_ids:
                rec.is_optional_accessory = True

    def _search_is_optional_accessory(self, operator, value):
        ids = self.env['lighting.product'] \
            .search([('optional_ids', '!=', False)]).mapped('optional_ids.id')

        return [('id', 'in', ids)]

    # Required accessories tab
    required_ids = fields.Many2many(comodel_name='lighting.product', relation='lighting_product_required_rel',
                                    column1="product_id", column2='required_id',
                                    string='Mandatory accessories', track_visibility='onchange')

    parent_required_accessory_product_count = fields.Integer(compute='_compute_parent_required_accessory_product_count')

    @api.depends('required_ids')
    def _compute_parent_required_accessory_product_count(self):
        for record in self:
            record.parent_required_accessory_product_count = self.env['lighting.product'] \
                .search_count([('required_ids', '=', record.id)])

    is_required_accessory = fields.Boolean(string='Is required accessory',
                                           compute='_compute_is_required_accessory',
                                           search='_search_is_required_accessory')

    @api.depends('required_ids')
    def _compute_is_required_accessory(self):
        for rec in self:
            parent_ids = self.env['lighting.product'].search([('required_ids', '=', rec.id)])
            if parent_ids:
                rec.is_required_accessory = True

    def _search_is_required_accessory(self, operator, value):
        ids = self.env['lighting.product'] \
            .search([('required_ids', '!=', False)]).mapped('required_ids.id')

        return [('id', 'in', ids)]

    # Substitutes tab
    substitute_ids = fields.Many2many(comodel_name='lighting.product', relation='lighting_product_substitute_rel',
                                      column1='product_id', column2='substitute_id',
                                      string='Substitutes', track_visibility='onchange')

    # logistics tab
    tariff_item = fields.Char(string="Tariff item", track_visibility='onchange')
    assembler_id = fields.Many2one(comodel_name='lighting.assembler', ondelete='restrict',
                                   string='Assembler', track_visibility='onchange')
    supplier_ids = fields.One2many(comodel_name='lighting.product.supplier', inverse_name='product_id',
                                   string='Suppliers', copy=True, track_visibility='onchange')

    ibox_weight = fields.Float(string='IBox weight (Kg)', track_visibility='onchange')
    ibox_volume = fields.Float(string='IBox volume (cm³)', track_visibility='onchange')
    ibox_length = fields.Float(string='IBox length (cm)', track_visibility='onchange')
    ibox_width = fields.Float(string='IBox width (cm)', track_visibility='onchange')
    ibox_height = fields.Float(string='IBox height (cm)', track_visibility='onchange')

    mbox_qty = fields.Integer(string='Masterbox quantity', track_visibility='onchange')
    mbox_weight = fields.Float(string='Masterbox weight (kg)', track_visibility='onchange')
    mbox_length = fields.Float(string='Masterbox length (cm)', track_visibility='onchange')
    mbox_width = fields.Float(string='Masterbox width (cm)', track_visibility='onchange')
    mbox_height = fields.Float(string='Masterbox height (cm)', track_visibility='onchange')

    # marketing tab
    state_marketing = fields.Selection([
        ('O', 'Online'),
        ('N', 'New'),
        ('C', 'Cataloged'),
        ('ES', 'Until end of stock'),
        ('D', 'Discontinued'),
        ('H', 'Historical'),
    ], string='Marketing status', track_visibility='onchange')

    on_request = fields.Boolean(string='On request', track_visibility='onchange')

    effective_date = fields.Date(string='Effective date', track_visibility='onchange')
    marketing_comments = fields.Char(string='Comments', track_visibility='onchange')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_review', 'To review'),
        ('published', 'Published'),
    ], string='Status', default='draft', readonly=False, required=True, copy=False, track_visibility='onchange')

    # aux functions
    def _update_computed_description(self):
        for lang in self.env['res.lang'].search([('code', '!=', self.env.lang)]):
            en_trl = self.with_context(lang='en_US')._generate_description()
            non_en_trl = self.with_context(lang=lang.code)._generate_description()
            trl = self.env['ir.translation'].search([
                ('name', '=', 'lighting.product,description'),
                ('lang', '=', lang.code),
                ('res_id', '=', self.id)
            ])
            if not trl and lang.code != 'en_US':
                trl = self.env['ir.translation'].create({
                    'name': 'lighting.product,description',
                    'type': 'model',
                    'lang': lang.code,
                    'res_id': self.id,
                })

            self.env.cr.execute('update lighting_product set description=%s where id=%s', (en_trl, self.id,))
            trl.with_context(lang=None).write({
                'state': 'translated',
                # 'source': en_trl,
                'src': en_trl,
                'value': non_en_trl, })

    # inherites base functions
    @api.multi
    @api.constrains('reference')
    def _check_reference_spaces(self):
        for rec in self:
            if rec.reference != rec.reference.strip():
                raise ValidationError(
                    _('The reference has trailing and/or leading spaces, plese remove them before saving.'))

    @api.multi
    @api.constrains('is_composite', 'required_ids')
    def _check_composite_product(self):
        for rec in self:
            if not rec.is_composite and rec.required_ids:
                raise ValidationError(
                    _("Only the composite products can have required accessories. Enable 'is_composite' "
                      "field or remove the required accessories associated."))

            if rec.is_composite and not rec.required_ids:
                raise ValidationError(
                    _("You cannot have a composite product without required accessories"))

    @api.constrains('product_group_id')
    def _check_product_group(self):
        if self.product_group_id.child_ids:
            raise ValidationError(_("You cannot assign products to a grup with childs. "
                                    "The group must not have childs and be empty or already contain products"))

    @api.multi
    @api.constrains('optional_ids', 'required_ids')
    def _check_composite_product(self):
        for rec in self:
            if rec in rec.required_ids:
                raise ValidationError(
                    _("The current reference cannot be defined as a required accessory"))

            if rec in rec.optional_ids:
                raise ValidationError(
                    _("The current reference cannot be defined as a recomended accessory"))

    @api.model
    def create(self, values):
        res = super().create(values)
        if res.description == 'false':
            res.description = False
        if 'description' in values:
            res._update_computed_description()

        return res

    @api.multi
    def write(self, values):
        res = super().write(values)
        if 'description' in values:
            self._update_computed_description()

        return res

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {},
                       reference=_('%s (copy)') % self.reference,
                       ean=False,
                       )

        return super(LightingProduct, self).copy(default)
