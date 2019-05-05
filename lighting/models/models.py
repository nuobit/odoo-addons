# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree

from collections import OrderedDict


#### auxiliary functions
def float2text(f, decs=2):
    if f == int(f):
        return '%i' % int(f)
    else:
        return ("{0:.%if}" % decs).format(f)


## main model
class LightingProduct(models.Model):
    _name = 'lighting.product'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'reference'
    _order = 'sequence,reference'
    _description = 'Product'

    # Common data
    reference = fields.Char(string='Reference', required=True, track_visibility='onchange')
    description = fields.Char(compute='_compute_description', string='Description', readonly=True,
                              help="Description dynamically generated from product data",
                              translate=True, store=True, track_visibility='onchange')

    @api.depends('category_id.name',
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
            data.append(self.category_id.name)

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
    family_ids = fields.Many2many(comodel_name='lighting.product.family',
                                  relation='lighting_product_family_rel', string='Families',
                                  track_visibility='onchange')
    catalog_ids = fields.Many2many(comodel_name='lighting.catalog', relation='lighting_product_catalog_rel',
                                   string='Catalogs', track_visibility='onchange')

    category_id = fields.Many2one(comodel_name='lighting.product.category',
                                  string='Category', required=True,
                                  ondelete='restrict', track_visibility='onchange')

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
    corrosion_resistance = fields.Boolean(string="Corrosion resistance", track_visibility='onchange')
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
    recessing_box_included = fields.Boolean(string='Cut hole box included', track_visibility='onchange')
    recess_dimension_ids = fields.One2many(comodel_name='lighting.product.recessdimension',
                                           inverse_name='product_id', string='Cut hole dimensions',
                                           copy=True, track_visibility='onchange')
    ecorrae_category_id = fields.Many2one(comodel_name='lighting.product.ecorraecategory', ondelete='restrict',
                                          string='ECORRAE I category', track_visibility='onchange')
    ecorrae2_category_id = fields.Many2one(comodel_name='lighting.product.ecorraecategory', ondelete='restrict',
                                           string='ECORRAE II category', track_visibility='onchange')
    ecorrae = fields.Float(string='ECORRAE I', track_visibility='onchange')
    ecorrae2 = fields.Float(string='ECORRAE II', track_visibility='onchange')

    periodic_maintenance = fields.Boolean(string='Periodic maintenance', track_visibility='onchange')
    anchorage_included = fields.Boolean(string='Anchorage included', track_visibility='onchange')
    post_included = fields.Boolean(string='Post included', track_visibility='onchange')
    post_with_inspection_chamber = fields.Boolean(string='Post with inspection chamber', track_visibility='onchange')

    emergency_light = fields.Boolean(string='Emergency light', help="Luminarie with emergency light",
                                     track_visibility='onchange')
    average_emergency_time = fields.Float(string='Average emergency time (h)', track_visibility='onchange')

    flammable_surfaces = fields.Boolean(string='Flammable surfaces', track_visibility='onchange')

    photobiological_risk_group_id = fields.Many2one(comodel_name='lighting.product.photobiologicalriskgroup',
                                                    ondelete='restrict',
                                                    string='Photobiological risk group', track_visibility='onchange')

    mechanical_screwdriver = fields.Boolean(string='Electric screwdriver', track_visibility='onchange')

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
    accessory_ids = fields.Many2many(comodel_name='lighting.product', relation='lighting_product_accessory_rel',
                                     column1="product_id", column2='accessory_id',
                                     domain=[('category_id.is_accessory', '=', True)],
                                     string='Accessories', track_visibility='onchange')

    # Required accessories tab
    required_ids = fields.Many2many(comodel_name='lighting.product', relation='lighting_product_required_rel',
                                    column1="product_id", column2='required_id',
                                    domain=[('category_id.is_accessory', '=', True)],
                                    string='Required', track_visibility='onchange')

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
    discontinued_by_supplier = fields.Boolean(string='Discontinued by supplier', track_visibility='onchange')
    discontinued_soon = fields.Boolean(string='Discontinued soon', track_visibility='onchange')
    until_end_stock = fields.Boolean(string='Until end of stock', track_visibility='onchange')
    on_request = fields.Boolean(string='On request', track_visibility='onchange')
    state_id = fields.Many2one(comodel_name='lighting.product.state', ondelete='restrict', string='State',
                               track_visibility='onchange')
    effective_date = fields.Date(string='Effective date', track_visibility='onchange')
    marketing_comments = fields.Char(string='Comments', track_visibility='onchange')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_review', 'To review'),
        ('published', 'Published'),
        ('discontinued', 'Discontinued'),
    ], string='Status', default='draft', readonly=False, required=True, copy=False, track_visibility='onchange')

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {},
                       reference=_('%s (copy)') % self.reference,
                       ean=False,
                       )

        return super(LightingProduct, self).copy(default)

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

    @api.multi
    @api.constrains('reference')
    def _check_reference_spaces(self):
        for rec in self:
            if rec.reference != rec.reference.strip():
                raise ValueError(
                    _('The reference has trailing and/or leading spaces, plese remove them before saving.'))

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


######### common data
class LightingEnergyEfficiency(models.Model):
    _name = 'lighting.energyefficiency'
    _order = 'sequence'

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")
    name = fields.Char(string='Description', required=True)

    color = fields.Integer(string='Color Index')

    _sql_constraints = [('name_uniq', 'unique (name)', 'The energy efficiency must be unique!'),
                        ]

    @api.multi
    def unlink(self):
        fields = ['efficiency_ids', 'lamp_included_efficiency_ids']
        for f in fields:
            records = self.env['lighting.product'].search([(f, 'in', self.ids)])
            if records:
                raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(LightingEnergyEfficiency, self).unlink()


class LightingDimensionType(models.Model):
    _name = 'lighting.dimension.type'
    _order = 'name'

    name = fields.Char(string='Name', required=True, translate=True)
    uom = fields.Char(string='Uom', help='Unit of mesure')
    description = fields.Char(string='Internal description')

    _sql_constraints = [('name_uniq', 'unique (name, uom)', 'The dimension name must be unique!'),
                        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '%s (%s)' % (record.name, record.uom)
            vals.append((record.id, name))

        return vals


########### description tab
class LightingProductMaterial(models.Model):
    _name = 'lighting.product.material'
    _order = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', required=True, translate=True)

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count([
                '|', '|', '|', '|', ('body_material_ids', '=', record.id),
                ('diffusor_material_ids', '=', record.id), ('frame_material_ids', '=', record.id),
                ('reflector_material_ids', '=', record.id), ('blade_material_ids', '=', record.id)])

    _sql_constraints = [('name_uniq', 'unique (name)', 'The material name must be unique!'),
                        ('code_uniq', 'unique (code)', 'The material code must be unique!'),
                        ]

    @api.multi
    def unlink(self):
        fields = ['body_material_ids', 'diffusor_material_ids', 'frame_material_ids',
                  'reflector_material_ids', 'blade_material_ids']
        for f in fields:
            records = self.env['lighting.product'].search([(f, 'in', self.ids)])
            if records:
                raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(LightingProductMaterial, self).unlink()


###### Electrical characteristics tab
class LightingProductProtectionClass(models.Model):
    _name = 'lighting.product.protectionclass'
    _order = 'name'

    name = fields.Char(string='Class', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The protection class must be unique!'),
                        ]


class LightingProductFrequency(models.Model):
    _name = 'lighting.product.frequency'
    _order = 'name'

    name = fields.Char(string='Frequency', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The frequency must be unique!'),
                        ]


class LightingProductDimmable(models.Model):
    _name = 'lighting.product.dimmable'
    _order = 'name'

    name = fields.Char(string='Dimmable', required=True, translate=True)

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count([('dimmable_ids', '=', record.id)])

    _sql_constraints = [('name_uniq', 'unique (name)', 'The dimmable must be unique!'),
                        ]

    @api.multi
    def unlink(self):
        records = self.env['lighting.product'].search([('dimmable_ids', 'in', self.ids)])
        if records:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(LightingProductDimmable, self).unlink()


class LightingProductAuxiliaryEquipment(models.Model):
    _name = 'lighting.product.auxiliaryequipment'
    _order = 'name'

    name = fields.Char(string='Auxiliary equipment', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The auxiliary equipment must be unique!'),
                        ]

    @api.multi
    def unlink(self):
        records = self.env['lighting.product'].search([('auxiliary_equipment_ids', 'in', self.ids)])
        if records:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(LightingProductAuxiliaryEquipment, self).unlink()


class LightingProductAuxiliaryEquipmentModel(models.Model):
    _name = 'lighting.product.auxiliaryequipmentmodel'
    _rec_name = 'reference'
    _order = 'product_id,date desc'

    reference = fields.Char(string='Reference')
    brand_id = fields.Many2one(comodel_name='lighting.product.auxiliaryequipmentbrand',
                               ondelete='restrict', string='Brand', required=True)
    date = fields.Date(string='Date')

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')

    _sql_constraints = [('prodate_uniq', 'unique (product_id, date)',
                         'The date must be unique!'),
                        ]


class LightingProductAuxiliaryEquipmentBrand(models.Model):
    _name = 'lighting.product.auxiliaryequipmentbrand'
    _order = 'name'

    name = fields.Char(string='Auxiliary equipment brand', required=True, translate=False)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The auxiliary equipment brand must be unique!'),
                        ]


class LightingProductSensor(models.Model):
    _name = 'lighting.product.sensor'
    _order = 'name'

    name = fields.Char(string='Sensor', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The sensor must be unique!'),
                        ]

    @api.multi
    def unlink(self):
        records = self.env['lighting.product'].search([('sensor_ids', 'in', self.ids)])
        if records:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(LightingProductSensor, self).unlink()


###########  Lighting characteristics tab

class LightingProductLedChip(models.Model):
    _name = 'lighting.product.ledchip'
    _rec_name = 'reference'
    _order = 'source_line_id,date desc'

    reference = fields.Char(string='Reference')
    brand_id = fields.Many2one(comodel_name='lighting.product.ledbrand',
                               ondelete='restrict', string='Brand', required=True)
    date = fields.Date(string='Date')

    source_line_id = fields.Many2one(comodel_name='lighting.product.source.line', ondelete='cascade',
                                     string='Source line')

    _sql_constraints = [('ledchip_uniq', 'unique (source_line_id, date)', 'The chip date must be unique!'),
                        ]


class LightingProductLedBrand(models.Model):
    _name = 'lighting.product.ledbrand'
    _order = 'name'

    name = fields.Char(string='LED brand', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The LED brand must be unique!'),
                        ]


###########  Physical characteristics tab
class LightingProductDimension(models.Model):
    _name = 'lighting.product.dimension'
    _rec_name = 'type_id'
    _order = 'sequence'

    type_id = fields.Many2one(comodel_name='lighting.dimension.type', ondelete='restrict', string='Dimension',
                              required=True)
    value = fields.Float(string='Value', required=True)
    sequence = fields.Integer(required=True, default=1,
                              help="The sequence field is used to define order in which the dimension lines are sorted")

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')


class LightingProductRecessDimension(models.Model):
    _name = 'lighting.product.recessdimension'
    _rec_name = 'type_id'
    _order = 'sequence'

    type_id = fields.Many2one(comodel_name='lighting.dimension.type', ondelete='restrict', string='Dimension',
                              required=True)
    value = fields.Float(string='Value', required=True)
    sequence = fields.Integer(required=True, default=1,
                              help="The sequence field is used to define order in which the recess dimension lines are sorted")

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')


class LightingProductEcorraeCategory(models.Model):
    _name = 'lighting.product.ecorraecategory'
    _order = 'name'

    name = fields.Char(string='Description', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The ecorrae category description must be unique!'),
                        ]


class LightingProductPhotobiologicalRiskGroup(models.Model):
    _name = 'lighting.product.photobiologicalriskgroup'
    _order = 'name'

    name = fields.Char(string='Description', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The photobiological risk group description must be unique!'),
                        ]


class LightingProductFanWattage(models.Model):
    _name = 'lighting.product.fanwattage'
    _rec_name = 'wattage'

    wattage = fields.Float(string='Wattage (W)', required=True)

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')

    _sql_constraints = [
        ('wattage_product_uniq', 'unique (product_id, wattage)', 'There are duplicated wattages on the same product!'),
    ]

    @api.constrains('wattage')
    def _check_wattage(self):
        for rec in self:
            if rec.wattage == 0:
                raise ValidationError("The fan wattage, if defined, cannot be 0")


########### sources tab
class LightingProductSource(models.Model):
    _name = 'lighting.product.source'
    _rec_name = 'relevance'
    _order = 'sequence'

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")

    relevance = fields.Selection([('main', 'Main'), ('aux', 'Auxiliary')], string='Relevance', required=True,
                                 default='main')
    num = fields.Integer(string='Number of sources', default=1)
    lampholder_id = fields.Many2one(comodel_name='lighting.product.source.lampholder', ondelete='restrict',
                                    string='Lampholder')
    lampholder_technical_id = fields.Many2one(comodel_name='lighting.product.source.lampholder', ondelete='restrict',
                                              string='Technical lampholder')

    line_ids = fields.One2many(comodel_name='lighting.product.source.line', inverse_name='source_id', string='Lines',
                               copy=True)

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')

    ## computed fields
    line_display = fields.Char(compute='_compute_line_display', string='Description')

    @api.depends('line_ids')
    def _compute_line_display(self):
        for rec in self:
            res = []
            for l in rec.line_ids.sorted(lambda x: x.sequence):
                line = [l.type_id.code]

                if l.is_integrated or l.is_lamp_included:
                    if l.color_temperature_id:
                        line.append("%iK" % l.color_temperature_id.value)
                    if l.luminous_flux_display:
                        line.append("%sLm" % l.luminous_flux_display)
                    if l.is_led and l.cri_min:
                        line.append("%iCRI" % l.cri_min)

                if l.wattage_display:
                    line.append("(%s)" % l.wattage_display)

                res.append(' '.join(line))

            if res != []:
                rec.line_display = " / ".join(res)


class LightingProductSourceLine(models.Model):
    _name = 'lighting.product.source.line'
    _rec_name = 'type_id'
    _order = 'sequence'

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")

    type_id = fields.Many2one(comodel_name='lighting.product.source.type', ondelete='restrict', string='Type',
                              required=True)

    wattage = fields.Float(string='Wattage')
    is_max_wattage = fields.Boolean(string='Is max. Wattage')
    wattage_magnitude = fields.Selection([('w', 'W'), ('wm', 'W/m')], string='Wattage magnitude', default='w')

    @api.constrains('wattage', 'type_id')
    def _check_wattage(self):
        for rec in self:
            if rec.type_id.is_integrated and rec.wattage <= 0:
                raise ValidationError(
                    "%s: The wattage on line %s must be greater than 0 if source type is integrated" % (
                        rec.source_id.product_id.display_name,
                        rec.type_id.display_name))

    luminous_flux1 = fields.Integer(string='Luminous flux 1 (Lm)')
    luminous_flux2 = fields.Integer(string='Luminous flux 2 (Lm)')
    color_temperature_id = fields.Many2one(string='Color temperature (K)',
                                           comodel_name='lighting.product.color.temperature', ondelete='cascade')

    cri_min = fields.Integer(string='CRI', help='Minimum color rendering index', track_visibility='onchange')

    is_led = fields.Boolean(related='type_id.is_led')
    color_consistency = fields.Float(string='Color consistency')
    special_spectrum = fields.Selection(selection=[
        ('meat', 'Meat'), ('fashion', 'Fashion'),
        ('multifood', 'Multi Food'), ('bread', 'Bread'),
        ('fish', 'Fish'), ('vegetable', 'Vegetable'),
        ('blue', _('Blue')), ('orange', _('Orange')),
        ('green', _('Green')), ('red', _('Red')),
        ('purple', _('Purple')), ('pink', _('Pink')),
    ], string='Special spectrum')
    led_chip_ids = fields.One2many(comodel_name='lighting.product.ledchip',
                                   inverse_name='source_line_id', string='Chip', copy=True)

    efficiency_ids = fields.Many2many(comodel_name='lighting.energyefficiency',
                                      relation='lighting_product_source_energyefficiency_rel',
                                      string='Energy efficiency')

    is_integrated = fields.Boolean(related='type_id.is_integrated')
    is_lamp_included = fields.Boolean(string='Lamp included?')
    lamp_included_efficiency_ids = fields.Many2many(comodel_name='lighting.energyefficiency',
                                                    relation='lighting_product_source_lampenergyefficiency_rel',
                                                    string='Lamp included efficiency')

    ## computed fields
    wattage_display = fields.Char(compute='_compute_wattage_display', string='Wattage (W)')

    def prepare_wattage_str(self, mult=1, is_max_wattage=None):
        self.ensure_one()

        if is_max_wattage is None:
            is_max_wattage = self.is_max_wattage

        wattage_magnitude_option = dict(
            self.fields_get(['wattage_magnitude'], ['selection']).get('wattage_magnitude').get('selection'))

        res = []
        if self.wattage > 0:
            wattage_str = float2text(self.wattage)
            if mult > 1:
                wattage_str = '%ix%s' % (mult, wattage_str)

            if self.wattage_magnitude:
                wattage_str += wattage_magnitude_option.get(self.wattage_magnitude)
            res.append(wattage_str)

        if is_max_wattage:
            res.append(_('max.'))

        if res != []:
            return " ".join(res)
        else:
            return False

    @api.depends('wattage', 'is_max_wattage', 'wattage_magnitude')
    def _compute_wattage_display(self):
        for rec in self:
            rec.wattage_display = rec.prepare_wattage_str()

    luminous_flux_display = fields.Char(compute='_compute_luminous_flux_display', string='Luminous flux (Lm)')

    @api.depends('luminous_flux1', 'luminous_flux2')
    def _compute_luminous_flux_display(self):
        for rec in self:
            res = []
            if rec.luminous_flux1:
                res.append(float2text(rec.luminous_flux1))

            if rec.luminous_flux2:
                res.append(float2text(rec.luminous_flux2))

            if res != []:
                rec.luminous_flux_display = "-".join(res)

    source_id = fields.Many2one(comodel_name='lighting.product.source', ondelete='cascade', string='Source')


########### beams tab
class LightingProductBeam(models.Model):
    _name = 'lighting.product.beam'
    _order = 'sequence'

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")

    num = fields.Integer(string='Number of beams', required=True, default=1)

    photometric_distribution_ids = fields.Many2many(comodel_name='lighting.product.beam.photodistribution',
                                                    relation='lighting_product_beam_photodistribution_rel',
                                                    string='Photometric distributions')

    dimension_ids = fields.One2many(comodel_name='lighting.product.beam.dimension', inverse_name='beam_id',
                                    string='Dimensions', copy=True)

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')

    ## computed fields
    dimensions_display = fields.Char(compute='_compute_dimensions_display', string='Dimensions')

    @api.depends('dimension_ids')
    def _compute_dimensions_display(self):
        for rec in self:
            res = []
            for dimension in rec.dimension_ids.sorted(lambda x: x.sequence):
                res.append('%s: %g' % (dimension.type_id.display_name, dimension.value))

            rec.dimensions_display = ', '.join(res)


class LightingProductBeamPhotometricDistribution(models.Model):
    _name = 'lighting.product.beam.photodistribution'
    _order = 'name'

    name = fields.Char(string='Description', required=True, translate=True)

    color = fields.Integer(string='Color Index')

    _sql_constraints = [('name_uniq', 'unique (name)', 'The photometric distribution name must be unique!'),
                        ]

    @api.multi
    def unlink(self):
        records = self.env['lighting.product'].search([('photometric_distribution_ids', 'in', self.ids)])
        if records:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(LightingProductBeamPhotometricDistribution, self).unlink()


class LightingProductBeamDimension(models.Model):
    _name = 'lighting.product.beam.dimension'
    _order = 'sequence'

    type_id = fields.Many2one(comodel_name='lighting.dimension.type', ondelete='restrict', string='Dimension',
                              required=True)
    value = fields.Float(string='Value', required=True)
    sequence = fields.Integer(required=True, default=1,
                              help="The sequence field is used to define order in which the dimension lines are sorted")

    beam_id = fields.Many2one(comodel_name='lighting.product.beam', ondelete='cascade', string='Beam')


class LightingLanguage(models.Model):
    _name = 'lighting.language'
    _order = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Language', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The language must be unique!'),
                        ('code_uniq', 'unique (code)', 'The language code must be unique!'),
                        ]


########### logistics tab
class LightingAssembler(models.Model):
    _name = 'lighting.assembler'
    _order = 'name'

    name = fields.Char(string='Assembler', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The assembler must be unique!'),
                        ]


class LightingProductSupplier(models.Model):
    _name = 'lighting.product.supplier'
    _rec_name = 'supplier_id'
    _order = 'sequence'

    sequence = fields.Integer(required=True, default=1,
                              help="The sequence field is used to define the priority of suppliers")
    supplier_id = fields.Many2one(comodel_name='lighting.supplier', ondelete='restrict', string='Supplier',
                                  required=True)
    reference = fields.Char(string="Reference")

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')


class LightingSupplier(models.Model):
    _name = 'lighting.supplier'
    _order = 'name'

    name = fields.Char(string='Description', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The supplier description must be unique!'),
                        ]


########### marketing tab
class LightingProductState(models.Model):
    _name = 'lighting.product.state'
    _order = 'name'

    name = fields.Char(string='State', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The state description must be unique!'),
                        ]
