# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree

#### auxiliary functions
def float2text(f, decs=2):
    if f == int(f):
        return '%i' % int(f)
    else:
        return ("{0:.%if}" % decs).format(f)


## main model
class LightingProduct(models.Model):
    _name = 'lighting.product'
    _rec_name = 'reference'
    _order = 'reference'

    # Common data
    reference = fields.Char(string='Reference', required=True)
    description = fields.Char(compute='_compute_description', string='Description', readonly=True,
                                   help="Description dynamically generated from product data", store=True)

    @api.depends('type_ids.name', 'family_ids.name', 'catalog_ids.description_show_ip', 'ip', 'ip2',
                 'dimmable_ids.name',
                 'source_ids.lampholder_id.code',
                 'source_ids.line_ids.type_id.code',
                 'source_ids.line_ids.type_id.description_text',
                 'source_ids.line_ids.wattage',
                 'source_ids.line_ids.wattage_magnitude',
                 'source_ids.line_ids.luminous_flux1',
                 'source_ids.line_ids.luminous_flux2',
                 'source_ids.line_ids.color_temperature',
                 'finish_id.name')
    def _compute_description(self):
        for rec in self:
            data = []
            if rec.type_ids:
                data.append(','.join(rec.type_ids.mapped('name')))

            if rec.family_ids:
                data.append(','.join(rec.family_ids.mapped('name')))

            if rec.catalog_ids:
                ip_catalogs = rec.catalog_ids.filtered(lambda x: x.description_show_ip)
                if ip_catalogs:
                    data_ip = []
                    for ipx in ('ip', 'ip2'):
                        ip = getattr(rec, ipx)
                        if ip:
                            prefix = self.fields_get([ipx], ['string']).get(ipx).get('string')
                            data_ip.append('%s %i' % (prefix, ip))
                    if data_ip:
                        data.append(','.join(data_ip))

            if rec.dimmable_ids:
                data.append(','.join(rec.dimmable_ids.mapped('name')))

            data_sources = []
            for source in rec.source_ids:
                type_d = {}
                for line in source.line_ids:
                    is_integrated = line.type_id.is_integrated
                    if is_integrated not in type_d:
                        type_d[is_integrated] = []
                    type_d[is_integrated].append(line)

                for is_integrated, lines in type_d.items():
                    data_source = []
                    if is_integrated:
                        data_lines = []
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

                            if line.color_temperature:
                                data_line.append('%sK' % line.color_temperature)

                            if data_line:
                                data_lines.append(' '.join(data_line))
                        if data_lines:
                            data_source.append(','.join(data_lines))
                    else:
                        if source.lampholder_id:
                            data_source.append(source.lampholder_id.code)

                        wattage_d = {}
                        for line in lines:
                            if line.wattage > 0 and line.wattage_magnitude:
                                if line.wattage_magnitude not in wattage_d:
                                    wattage_d[line.wattage_magnitude] = []
                                wattage_d[line.wattage_magnitude].append(line)

                        data_lines = []
                        for lines in wattage_d.values():
                            line_max = sorted(lines, key=lambda x: x.wattage, reverse=True)[0]
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

            if rec.finish_id:
                data.append(rec.finish_id.name)

            if data:
                rec.description = ' '.join(data)

    description_manual = fields.Char(string='Description (manual)', help='Manual description', translate=True)

    ean = fields.Char(string='EAN', required=False, index=True)
    family_ids = fields.Many2many(comodel_name='lighting.product.family',
                                  relation='lighting_product_family_rel', string='Families')
    catalog_ids = fields.Many2many(comodel_name='lighting.catalog', relation='lighting_product_catalog_rel', string='Catalogs')
    type_ids = fields.Many2many(comodel_name='lighting.product.type', relation='lighting_product_type_rel', string='Types')

    is_accessory = fields.Boolean(string='Is accessory')
    is_component = fields.Boolean(string='Is component')

    last_update = fields.Date(string='Last modified on')

    _sql_constraints = [ ('reference_uniq', 'unique (reference)', 'The reference must be unique!'),
                         ('ean_uniq', 'unique (ean)', 'The EAN must be unique!')
        ]

    install_location = fields.Selection(selection=[('indoor', _('Indoor')), ('outdoor', _('Outdoor')), ('underwater', _('Underwater'))
                                ], string='Installation location')

    # Description tab
    application_ids = fields.Many2many(comodel_name='lighting.product.application',
                                       relation='lighting_product_application_rel', string='Applications')
    finish_id = fields.Many2one(comodel_name='lighting.product.finish', ondelete='restrict', string='Finish')

    body_material_ids = fields.Many2many(comodel_name='lighting.product.material', relation='lighting_product_body_material_rel', string='Body material')
    diffusor_material_ids = fields.Many2many(comodel_name='lighting.product.material', relation='lighting_product_diffusor_material_rel', string='Diffusor material')
    frame_material_ids = fields.Many2many(comodel_name='lighting.product.material', relation='lighting_product_frame_material_rel', string='Frame material')
    reflector_material_ids = fields.Many2many(comodel_name='lighting.product.material', relation='lighting_product_reflector_material_rel', string='Reflector material')
    blade_material_ids = fields.Many2many(comodel_name='lighting.product.material', relation='lighting_product_blade_material_rel', string='Blade material')

    ip = fields.Integer(string="IP")
    ip2 = fields.Integer(string="IP2")
    ik = fields.Selection(
        selection=[("%02d" % x, "%02d" % x) for x in range(11)], string='IK')

    static_pressure = fields.Float(string="Static pressure (kg)")
    dynamic_pressure = fields.Float(string="Dynamic pressure (kg)")
    dynamic_pressure_velocity = fields.Float(string="Dynamic pressure (km/h)")
    corrosion_resistance = fields.Boolean(string="Corrosion resistance")
    technical_comments = fields.Char(string='Technical comments')

    # electrical characteristics tab
    protection_class_id = fields.Many2one(comodel_name='lighting.product.protectionclass', ondelete='restrict', string='Protection class')
    frequency_id = fields.Many2one(comodel_name='lighting.product.frequency', ondelete='restrict', string='Frequency')
    dimmable_ids = fields.Many2many(comodel_name='lighting.product.dimmable', relation='lighting_product_dimmable_rel', string='Dimmables')
    auxiliary_equipment_ids = fields.Many2many(comodel_name='lighting.product.auxiliaryequipment', relation='lighting_product_auxiliary_equipment_rel', string='Auxiliary equipment')
    auxiliary_equipment_model_ids = fields.One2many(comodel_name='lighting.product.auxiliaryequipmentmodel',
                                        inverse_name='product_id', string='Auxiliary equipment models', copy=True)
    auxiliary_equipment_model_alt = fields.Char(string='Auxiliary equipment model alternative')
    input_voltage_id = fields.Many2one(comodel_name='lighting.product.voltage', ondelete='restrict', string='Input voltage')
    input_current = fields.Float(string='Input current (mA)')
    output_voltage_id = fields.Many2one(comodel_name='lighting.product.voltage', ondelete='restrict', string='Output voltage')
    output_current = fields.Float(string='Output current (mA)')

    total_wattage = fields.Float(compute='_compute_total_wattage',
                                 inverse='_inverse_total_wattage',
                                 string='Total wattage (W)', help='Total power consumed by the luminaire', store=True)
    total_wattage_auto = fields.Boolean(string='Autocalculate', help='Autocalculate total wattage', default=True)

    @api.depends('total_wattage_auto', 'source_ids.line_ids.wattage', 'source_ids.line_ids.type_id',
                 'source_ids.line_ids.type_id.is_integrated')
    def _compute_total_wattage(self):
        for rec in self:
            if rec.total_wattage_auto:
                rec.total_wattage = 0
                line_l = rec.source_ids.mapped('line_ids').filtered(lambda x: x.type_id.is_integrated)
                for line in line_l:
                    if line.wattage <= 0:
                        raise ValidationError("%s: The source line %s has invalid wattage" % (rec.display_name,
                                                                                              line.type_id.display_name))
                    rec.total_wattage += line.source_id.num*line.wattage

    def _inverse_total_wattage(self):
        ## dummy method. It allows to update calculated field
        pass

    power_factor_min = fields.Float(string='Minimum power factor')
    power_switches = fields.Integer(string='Power switches', help="Number of power switches")

    usb_ports = fields.Integer(string='USB ports', help="Number of USB ports")
    usb_voltage = fields.Float(string='USB voltage')
    usb_current = fields.Float(string='USB current')

    sensor_ids = fields.Many2many(comodel_name='lighting.product.sensor', relation='lighting_product_sensor_rel',
                                    string='Sensors')

    battery_autonomy = fields.Float(string='Battery autonomy (h)')
    battery_charge_time = fields.Float(string='Battery charge time (h)')
    surface_temperature = fields.Float(string='Surface temperature (ºC)')
    operating_temperature_min = fields.Float(string='Minimum operating temperature (ºC)')
    operating_temperature_max = fields.Float(string='Maximum operating temperature (ºC)')

    glow_wire_temperature = fields.Float(string='Glow wire temperature (ºC)')

    #light characteristics tab
    total_nominal_flux = fields.Float(string='Total flux (Lm)', help='Luminaire total nominal flux')
    cri_min = fields.Integer(string='CRI', help='Minimum color rendering index')
    ugr_max = fields.Integer(string='UGR', help='Maximum unified glare rating')

    lifetime = fields.Integer(string='Lifetime (h)')

    led_lifetime_l = fields.Integer(string='LED lifetime L')
    led_lifetime_b = fields.Integer(string='LED lifetime B')

    # Physical characteristics
    weight = fields.Float(string='Weight (kg)')
    dimension_ids = fields.One2many(comodel_name='lighting.product.dimension', inverse_name='product_id', string='Dimensions', copy=True)

    cable_outlets = fields.Integer(string='Cable outlets', help="Number of cable outlets")
    lead_wires = fields.Integer(string='Lead wires supplied', help="Number of lead wires supplied")
    lead_wire_length = fields.Float(string='Length of the lead wire supplied (mm)')
    inclination_angle_max = fields.Float(string='Maximum inclination angle (º)')
    rotation_angle_max = fields.Float(string='Maximum rotation angle (º)')
    recessing_box_included = fields.Boolean(string='Recessing box included')
    recess_dimension_ids = fields.One2many(comodel_name='lighting.product.recessdimension', inverse_name='product_id', string='Recess dimensions', copy=True)
    ecorrae_category_id = fields.Many2one(comodel_name='lighting.product.ecorraecategory', ondelete='restrict',
                                          string='ECORRAE I category')
    ecorrae2_category_id = fields.Many2one(comodel_name='lighting.product.ecorrae2category', ondelete='restrict',
                                          string='ECORRAE II category')
    ecorrae = fields.Float(string='ECORRAE I')
    ecorrae2 = fields.Float(string='ECORRAE II')

    periodic_maintenance = fields.Boolean(string='Periodic maintenance')
    anchorage_included = fields.Boolean(string='Anchorage included')
    post_included = fields.Boolean(string='Post included')
    post_with_inspection_chamber = fields.Boolean(string='Post with inspection chamber')

    emergency_light = fields.Boolean(string='Emergency light', help="Luminarie with emergency light")
    average_emergency_time = fields.Float(string='Average emergency time (h)')

    flammable_surfaces = fields.Boolean(string='Flammable surfaces')

    photobiological_risk_group_id = fields.Many2one(comodel_name='lighting.product.photobiologicalriskgroup', ondelete='restrict',
                                         string='Photobiological risk group')

    mechanical_screwdriver = fields.Boolean(string='Mechanical screwdriver')

    fan_blades = fields.Integer(string='Fan blades', help='Number of fan blades')
    fan_control = fields.Selection(selection=[('remote', 'Remote control'), ('wall', 'Wall control')], string='Fan control type')
    fan_wattage_ids = fields.One2many(comodel_name='lighting.product.fanwattage', inverse_name='product_id', string='Fan wattages (W)', copy=True)

    # Sources tab
    source_ids = fields.One2many(comodel_name='lighting.product.source', inverse_name='product_id', string='Sources', copy=True)

    source_count = fields.Integer(compute='_compute_source_count', string='Total sources')

    @api.depends('source_ids')
    def _compute_source_count(self):
        for rec in self:
            rec.source_count = sum(rec.source_ids.mapped('num'))

    # Beams tab
    beam_ids = fields.One2many(comodel_name='lighting.product.beam', inverse_name='product_id', string='Beams', copy=True)

    beam_count = fields.Integer(compute='_compute_beam_count', string='Total beams')

    @api.depends('beam_ids')
    def _compute_beam_count(self):
        for rec in self:
            rec.beam_count = sum(rec.beam_ids.mapped('num'))

    # Attachment tab
    attachment_ids = fields.One2many(comodel_name='lighting.attachment', inverse_name='product_id', string='Attachments', copy=True)
    attachment_count = fields.Integer(compute='_compute_attachment_count', string='Attachment(s)')

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = self.env['lighting.attachment'].search_count([('product_id', '=', record.id)])

    # Components tab
    component_ids = fields.Many2many(comodel_name='lighting.product', relation='lighting_product_component_rel',
                                     column1="product_id", column2='component_id',
                                     domain=[('is_component', '=', True)],
                                     string='Components')

    # Accesories tab
    accessory_ids = fields.Many2many(comodel_name='lighting.product', relation='lighting_product_accessory_rel',
                                     column1="product_id", column2='accessory_id',
                                     domain=[('is_accessory', '=', True)],
                                     string='Accessories')

    # Substitutes tab
    substitute_ids = fields.Many2many(comodel_name='lighting.product', relation='lighting_product_substitute_rel',
                                      column1='product_id', column2='substitute_id',
                                      string='Substitutes')

    # logistics tab
    tariff_item = fields.Char(string="Tariff item")
    assembler_id = fields.Many2one(comodel_name='lighting.assembler', ondelete='restrict', string='Assembler')
    supplier_ids = fields.One2many(comodel_name='lighting.product.supplier', inverse_name='product_id',
                                           string='Suppliers', copy=True)

    ibox_weight = fields.Float(string='IBox weight (Kg)')
    ibox_volume = fields.Float(string='IBox volume (cm³)')
    ibox_length = fields.Float(string='IBox length (cm)')
    ibox_width = fields.Float(string='IBox width (cm)')
    ibox_height = fields.Float(string='IBox height (cm)')

    mbox_qty = fields.Integer(string='Masterbox quantity')
    mbox_weight = fields.Float(string='Masterbox weight (kg)')
    mbox_length = fields.Float(string='Masterbox length (cm)')
    mbox_width = fields.Float(string='Masterbox width (cm)')
    mbox_height = fields.Float(string='Masterbox height (cm)')

    # marketing tab
    discontinued_by_supplier = fields.Boolean(string='Discontinued by supplier')
    until_end_stock = fields.Boolean(string='Until end of stock')
    on_request = fields.Boolean(string='On request')
    state_id = fields.Many2one(comodel_name='lighting.product.state', ondelete='restrict', string='State')
    effective_date = fields.Date(string='Effective date')
    marketing_comments = fields.Char(string='Comments')

    ########### ETIM
    class_id = fields.Many2one(comodel_name='lighting.etim.class', ondelete='restrict', string='Class')
    feature_ids = fields.One2many(comodel_name='lighting.product.etim.feature',
                                   inverse_name='product_id', string='Features', copy=True)

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
                       ean=_('%s (copy)') % self.ean,
                       )

        return super(LightingProduct, self).copy(default)


######### common data
class LightingEnergyEfficiency(models.Model):
    _name = 'lighting.energyefficiency'
    _order = 'sequence'

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")
    name = fields.Char(string='Description', required=True)

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
                '|', '|', '|', '|', ('body_material_ids','=',record.id),
                ('diffusor_material_ids','=',record.id), ('frame_material_ids','=',record.id),
                ('reflector_material_ids','=',record.id), ('blade_material_ids','=',record.id)])

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

    source_line_id = fields.Many2one(comodel_name='lighting.product.source.line', ondelete='cascade', string='Source line')

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

    type_id = fields.Many2one(comodel_name='lighting.dimension.type', ondelete='restrict', string='Dimension', required=True)
    value = fields.Float(string='Value', required=True)
    sequence = fields.Integer(required=True, default=1,
        help="The sequence field is used to define order in which the dimension lines are sorted")

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')

class LightingProductRecessDimension(models.Model):
    _name = 'lighting.product.recessdimension'
    _rec_name = 'type_id'
    _order = 'sequence'

    type_id = fields.Many2one(comodel_name='lighting.dimension.type', ondelete='restrict', string='Recess dimension', required=True)
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

class LightingProductEcorrae2Category(models.Model):
    _name = 'lighting.product.ecorrae2category'
    _order = 'name'

    name = fields.Char(string='Description', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The ecorrae2 category description must be unique!'),
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

    _sql_constraints = [('wattage_product_uniq', 'unique (product_id, wattage)', 'There are duplicated wattages on the same product!'),
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

    relevance = fields.Selection([('main', 'Main'), ('aux', 'Auxiliary')], string='Relevance', required=True, default='main')
    num = fields.Integer(string='Number of sources', default=1)
    lampholder_id =  fields.Many2one(comodel_name='lighting.product.source.lampholder', ondelete='restrict', string='Lampholder')
    lampholder_technical_id = fields.Many2one(comodel_name='lighting.product.source.lampholder', ondelete='restrict',
                                    string='Technical lampholder')

    line_ids = fields.One2many(comodel_name='lighting.product.source.line', inverse_name='source_id', string='Lines', copy=True)

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')

    ## computed fields
    line_display = fields.Char(compute='_compute_line_display', string='Sources')

    @api.depends('line_ids')
    def _compute_line_display(self):
        for rec in self:
            res = []
            for l in rec.line_ids.sorted(lambda x: x.sequence):
                line = [l.type_id.code]
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

    type_id = fields.Many2one(comodel_name='lighting.product.source.type', ondelete='restrict', string='Type', required=True)

    wattage = fields.Float(string='Wattage')
    is_max_wattage = fields.Boolean(string='Is max. Wattage')
    wattage_magnitude = fields.Selection([('w', 'W'), ('wm', 'W/m')], string='Wattage magnitude', default='w')

    @api.constrains('wattage', 'type_id')
    def _check_wattage(self):
        for rec in self:
            if rec.type_id.is_integrated and rec.wattage <= 0:
                raise ValidationError("%s: The wattage on line %s must be greater than 0 if source type is integrated" % (rec.source_id.product_id.display_name,
                                                                                                                          rec.type_id.display_name))

    luminous_flux1 = fields.Integer(string='Luminous flux 1 (Lm)')
    luminous_flux2 = fields.Integer(string='Luminous flux 2 (Lm)')
    color_temperature = fields.Integer(string='Color temperature (K)')

    is_led = fields.Boolean(related='type_id.is_led')
    color_consistency = fields.Float(string='Color consistency')
    special_spectrum = fields.Selection(selection = [
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
            if mult>1:
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

    dimension_ids = fields.One2many(comodel_name='lighting.product.beam.dimension', inverse_name='beam_id', string='Dimensions', copy=True)

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')

    ## computed fields
    dimensions_display = fields.Char(compute='_compute_dimensions_display', string='Dimensions')

    @api.depends('dimension_ids')
    def _compute_dimensions_display(self):
        for rec in self:
            res = []
            for dimension in rec.dimension_ids.sorted(lambda x: x.sequence):
                res.append('%s: %f' % (dimension.type_id.display_name, dimension.value))

            rec.dimensions_display = ', '.join(res)

class LightingProductBeamPhotometricDistribution(models.Model):
    _name = 'lighting.product.beam.photodistribution'
    _order = 'name'

    name = fields.Char(string='Description', required=True, translate=True)

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

    type_id = fields.Many2one(comodel_name='lighting.dimension.type', ondelete='restrict', string='Dimension', required=True)
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

    name = fields.Char(string='Asssembler', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The assembler must be unique!'),
                        ]

class LightingProductSupplier(models.Model):
    _name = 'lighting.product.supplier'
    _rec_name = 'supplier_id'
    _order = 'sequence'

    sequence = fields.Integer(required=True, default=1,
                              help="The sequence field is used to define the priority of suppliers")
    supplier_id = fields.Many2one(comodel_name='lighting.supplier', ondelete='restrict', string='Supplier', required=True)
    reference = fields.Char(string="Supplier reference")

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

########## ETIM tab
class LightingProductETIMFeature(models.Model):
    _name = 'lighting.product.etim.feature'

    feature_id = fields.Many2one(comodel_name='lighting.etim.feature', ondelete='restrict', string='Feature')

    @api.onchange('feature_id')
    def feature_id_change(self):
        self.unit_id = self.product_id.class_id.feature_ids.filtered(
            lambda x: x['feature_id']==self.feature_id).unit_id
        feature_value_ids = self.product_id.class_id.feature_ids.filtered(
            lambda x: x['feature_id'] == self.feature_id).value_ids.mapped('value_id.id')

        return {'domain': {'unit_id': [('id', '=', self.unit_id.id)],
                           'a_value_id': [('id', 'in', feature_value_ids)]
                           },
                }

    feature_type = fields.Selection(related='feature_id.type', string="Type", readonly=True)

    unit_id = fields.Many2one(comodel_name='lighting.etim.unit', ondelete='restrict', string='Unit', readonly=True)
    has_unit = fields.Boolean(compute="_compute_has_unit")

    @api.depends('feature_id')
    def _compute_has_unit(self):
        for rec in self:
            unit_ids = self.product_id.class_id.feature_ids.filtered(
                lambda x: x['feature_id'] == self.feature_id).unit_id

            rec.has_unit = len(unit_ids) != 0

    a_value_id = fields.Many2one(comodel_name='lighting.etim.value', ondelete='restrict', string='Value')
    l_value = fields.Boolean('Value')
    n_value = fields.Float('Value')
    r1_value = fields.Float('Value 1')
    r2_value = fields.Float('Value 2')

    value = fields.Char(compute='_compute_value', string='Value', readonly=True)

    @api.depends('feature_id', 'a_value_id', 'l_value', 'n_value', 'r1_value', 'r2_value')
    def _compute_value(self):
        for rec in self:
            if rec.feature_id.type == 'A':
                rec.value = rec.a_value_id.display_name
            elif rec.feature_id.type == 'L':
                rec.value = 'True' if rec.l_value else 'False'
            elif rec.feature_id.type == 'N':
                rec.value = str(rec.n_value)
            elif rec.feature_id.type == 'R':
                range_str = []
                if rec.r1_value:
                    range_str.append(str(rec.r1_value))
                if rec.r2_value:
                    range_str.append(str(rec.r2_value))
                if range_str != []:
                    rec.value = ' - '.join(range_str)

    product_class_id = fields.Many2one(related='product_id.class_id', readonly=True)
    # @api.onchange('product_class_id')
    # def product_class_id_change(self):
    #     return {'domain': {'feature_id': [('id', 'in', self.product_id.class_id.feature_ids.mapped('feature_id.id'))]}}

    product_class_feature_ids = fields.One2many(comodel_name='lighting.etim.feature',
                                                compute="_product_class_feature_ids", readonly=True)

    @api.depends('product_class_id')
    def _product_class_feature_ids(self):
        for rec in self:
            rec.product_class_feature_ids = rec.product_id.class_id.feature_ids.mapped('feature_id')

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product', required=True)

    _sql_constraints = [
        ('feature_uniq', 'unique (feature_id, product_id)', 'Feature duplicated'),
        ]

########### ETIM

class LightingETIMUnit(models.Model):
    _name = 'lighting.etim.unit'

    code = fields.Char("Code", required=True)
    name = fields.Char("Description", required=True, translate=True)
    abbreviation = fields.Char("Abbreviation", required=True, translate=True)

    _sql_constraints = [ ('code', 'unique (code)', 'The code must be unique!'),
        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '[%s] %s (%s)' % (record.code, record.name, record.abbreviation)
            vals.append((record.id, name))

        return vals



class LightingETIMFeature(models.Model):
    _name = 'lighting.etim.feature'

    code = fields.Char("Code", required=True)
    name = fields.Char("Description", required=True, translate=True)
    type = fields.Selection([('N', 'Numeric'),
                             ('L', 'Logical'),
                             ('R', 'Range'),
                             ('A', 'Alphanumeric')], "Type", required=True)

    _sql_constraints = [ ('code', 'unique (code)', 'The code must be unique!'),
        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            vals.append((record.id, name))

        return vals

class LightingETIMValue(models.Model):
    _name = 'lighting.etim.value'

    code = fields.Char("Code", required=True)
    name = fields.Char("Description", required=True, translate=True)

    _sql_constraints = [ ('code', 'unique (code)', 'The code must be unique!'),
        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            vals.append((record.id, name))

        return vals

class LightingETIMGroup(models.Model):
    _name = 'lighting.etim.group'

    code = fields.Char("Code", required=True)
    name = fields.Char("Description", required=True, translate=True)

    _sql_constraints = [ ('code', 'unique (code)', 'The code must be unique!'),
        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            vals.append((record.id, name))

        return vals

class LightingETIMClass(models.Model):
    _name = 'lighting.etim.class'

    code = fields.Char("Code", required=True)
    name = fields.Char("Description", required=True, translate=True)
    version = fields.Integer("Version", required=True)
    change_code = fields.Char("Change code", required=True)

    status = fields.Char("Status", required=True)

    group_id = fields.Many2one(comodel_name='lighting.etim.group', ondelete='restrict', string='Group', required=True)

    synonim_ids = fields.One2many(comodel_name='lighting.etim.class.synonim',
                                   inverse_name='class_id', string='Synonims')

    feature_ids = fields.One2many(comodel_name='lighting.etim.class.feature',
                                   inverse_name='class_id', string='Features')

    _sql_constraints = [ ('code', 'unique (code)', 'The code must be unique!'),
        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            vals.append((record.id, name))

        return vals

class LightingETIMClassSynonim(models.Model):
    _name = 'lighting.etim.class.synonim'

    name = fields.Char("Synonim", required=True, translate=True)

    class_id = fields.Many2one(comodel_name='lighting.etim.class', ondelete='cascade', string='Class')


class LightingETIMClassFeature(models.Model):
    _name = 'lighting.etim.class.feature'

    sequence = fields.Integer("Order", required=True, default=1)

    change_code = fields.Char("Change code", required=True)

    feature_id = fields.Many2one(comodel_name='lighting.etim.feature', ondelete='restrict', string='Feature')
    unit_id = fields.Many2one(comodel_name='lighting.etim.unit', ondelete='restrict', string='Unit')

    value_ids = fields.One2many(comodel_name='lighting.etim.class.feature.value',
                                  inverse_name='feature_id', string='Values')

    class_id = fields.Many2one(comodel_name='lighting.etim.class', ondelete='cascade', string='Class')


class LightingETIMClassFeatureValue(models.Model):
    _name = 'lighting.etim.class.feature.value'

    sequence = fields.Integer("Order", required=True, default=1)

    change_code = fields.Char("Change code", required=True)

    value_id = fields.Many2one(comodel_name='lighting.etim.value', ondelete='restrict', string='Value')

    feature_id = fields.Many2one(comodel_name='lighting.etim.class.feature', ondelete='cascade', string='Feature')