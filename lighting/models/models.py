from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree

#### auxiliary funcntions
def float2text(f, decs=2):
    if f == int(f):
        return '%i' % int(f)
    else:
        return ("{0:.%if}" % decs).format(f)



## main model
class LightingProduct(models.Model):
    _name = 'lighting.product'
    #_rec_name = 'full_name'
    _rec_name = 'reference'

    # Common data
    reference = fields.Char(string='Reference', required=True, index=True, copy=False)
    description = fields.Char(string='Description', translate=True)  #required=True
    #full_name = fields.Char(compute='_compute_full_name', string='Product Name', search='_search_full_name')
    ean = fields.Char(string='EAN', required=True, index=True, copy=False)
    family_ids = fields.Many2many(comodel_name='lighting.product.family', relation='lighting_product_family_rel', string='Family')
    catalog_ids = fields.Many2many(comodel_name='lighting.catalog', relation='lighting_product_catalog_rel', string='Catalogs')
    type_id = fields.Many2one(comodel_name='lighting.product.type', ondelete='restrict', string='Type')


    install_location = fields.Selection(selection=[('indoor', _('Indoor')), ('outdoor', _('Outdoor')), ('underwater', _('Underwater'))
                                ], string='Installation location')

    # Description tab
    application_id = fields.Many2one(comodel_name='lighting.product.application', ondelete='restrict', string='Application')
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
    auxiliary_equipment_id = fields.Many2one(comodel_name='lighting.product.auxiliaryequipment', ondelete='restrict', string='Auxiliary equipment')
    auxiliary_equipment_model_id = fields.Many2one(comodel_name='lighting.product.auxiliaryequipmentmodel', ondelete='restrict',
                                          string='Auxiliary equipment model')
    auxiliary_equipment_model_alt_id = fields.Many2one(comodel_name='lighting.product.auxiliaryequipmentmodel', ondelete='restrict',
                                                string='Auxiliary equipment model alternative')
    input_voltage_id = fields.Many2one(comodel_name='lighting.product.voltage', ondelete='restrict', string='Input voltage')
    input_current = fields.Float(string='Input current (mA)')
    output_voltage_id = fields.Many2one(comodel_name='lighting.product.voltage', ondelete='restrict', string='Output voltage')
    output_current = fields.Float(string='Output current (mA)')

    total_wattage = fields.Float(string='Total wattage (W)', help='Total power consumed by the luminaire')
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

    color_consistency = fields.Float(string='Color consistency')

    led_brand_id = fields.Many2one(comodel_name='lighting.product.ledbrand', ondelete='restrict', string='LED brand')

    # Physical characteristics
    weight = fields.Float(string='Weight (kg)')
    dimension_ids = fields.One2many(comodel_name='lighting.product.dimension', inverse_name='product_id', string='Dimensions')

    cable_outlets = fields.Integer(string='Cable outlets', help="Number of cable outlets")
    lead_wires = fields.Integer(string='Lead wires supplied', help="Number of lead wires supplied")
    lead_wire_length = fields.Float(string='Length of the lead wire supplied (mm)')
    inclination_angle_max = fields.Float(string='Maximum inclination angle (º)')
    rotation_angle_max = fields.Float(string='Maximum rotation angle (º)')
    recessing_box_included = fields.Boolean(string='Recessing box included')
    recess_dimension_ids = fields.One2many(comodel_name='lighting.product.recessdimension', inverse_name='product_id', string='Recess dimensions')
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
    fan_wattage_ids = fields.One2many(comodel_name='lighting.product.fanwattage', inverse_name='product_id', string='Fan wattages (W)')

    # Sources tab
    source_ids = fields.One2many(comodel_name='lighting.product.source', inverse_name='product_id', string='Sources')

    source_count = fields.Integer(compute='_compute_source_count', string='Total sources')

    @api.depends('source_ids')
    def _compute_source_count(self):
        self.source_count = sum(self.source_ids.mapped('num'))

    # Beams tab
    beam_ids = fields.One2many(comodel_name='lighting.product.beam', inverse_name='product_id', string='Beams')

    beam_count = fields.Integer(compute='_compute_beam_count', string='Total beams')

    @api.depends('beam_ids')
    def _compute_beam_count(self):
        self.beam_count = sum(self.beam_ids.mapped('num'))

    # Attachment tab
    attachment_ids = fields.One2many(comodel_name='lighting.attachment', inverse_name='product_id', string='Attachments')
    attachment_count = fields.Integer(compute='_compute_attachment_count', string='Attachment(s)')

    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = self.env['lighting.attachment'].search_count([('product_id', '=', record.id)])

    # Accesories tab
    accessory_ids = fields.Many2many(comodel_name='lighting.product', relation='lighting_product_accessory_rel',
                                     column2='lighting_product_accessory_id', domain=[('type_id.is_accessory', '=', True)],string='Accessories')

    # Substitutes tab
    substitute_ids = fields.Many2many(comodel_name='lighting.product', relation='lighting_product_substitute_rel',
                                     column2='lighting_product_substitute_id', string='Substitutes')


    # logistics tab
    tariff_item = fields.Char(string="Tariff item")
    assembler_id = fields.Many2one(comodel_name='lighting.assembler', ondelete='restrict', string='Assembler')
    supplier_ids = fields.One2many(comodel_name='lighting.product.supplier', inverse_name='product_id',
                                           string='Suppliers')

    ibox_weight = fields.Float(string='IBox weight (Kg)')
    ibox_length = fields.Float(string='IBox length (cm)')
    ibox_width = fields.Float(string='IBox width (cm)')
    ibox_height = fields.Float(string='IBox height (cm)')

    mbox_qty = fields.Integer(string='Masterbox quantity')
    mbox_weight = fields.Float(string='Masterbox weight (kg)')
    mbox_length = fields.Float(string='Masterbox length (cm)')
    mbox_width = fields.Float(string='Masterbox width (cm)')
    mbox_height = fields.Float(string='Masterbox height (cm)')

    # marketing tab
    discontinued = fields.Boolean(string='Discontinued')
    discontinued_by_supplier = fields.Boolean(string='Discontinued by supplier')
    until_end_stock = fields.Boolean(string='Until end of stock')
    on_request = fields.Boolean(string='On request')
    obsolete = fields.Boolean(string='Obsolete')
    fixed_mrp  = fields.Boolean(string='Fixed MRP')
    seo_description = fields.Char(string='SEO description')
    url_description = fields.Char(string='URL description')
    state_id = fields.Many2one(comodel_name='lighting.product.state', ondelete='restrict', string='State')
    marketing_comments = fields.Char(string='Comments')

    _sql_constraints = [ ('reference_uniq', 'unique (reference)', 'The reference must be unique!'),
                         ('ean_uniq', 'unique (ean)', 'The EAN must be unique!')
        ]




######### common data
class LightingCatalog(models.Model):
    _name = 'lighting.catalog'

    name = fields.Char(string='Catalog', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The name of catalog must be unique!'),
                        ]

class LightingProductFamily(models.Model):
    _name = 'lighting.product.family'

    name = fields.Char(string='Family', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The family must be unique!'),
                        ]

class LightingProductType(models.Model):
    _name = 'lighting.product.type'

    name = fields.Char(string='Type', required=True, translate=True)
    is_accessory = fields.Boolean(string='Is accessory')

    '''
    field_ids = fields.Many2many(comodel_name='ir.model.fields', relation='lighting_product_type_model_fields_rel',
                                 domain=[('model_id.model', '=', 'lighting.product')],string='Fields')
    '''

    _sql_constraints = [('name_uniq', 'unique (name)', 'The type must be unique!'),
                        ]

class LightingEnergyEfficiency(models.Model):
    _name = 'lighting.energyefficiency'
    _order = 'sequence'

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")
    name = fields.Char(string='Description', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The energy efficiency must be unique!'),
                        ]


class LightingDimensionType(models.Model):
    _name = 'lighting.dimension.type'

    name = fields.Char(string='Description', required=True, translate=True)
    uom = fields.Char(string='Uom', help='Unit of mesure')

    _sql_constraints = [('name_uniq', 'unique (name, uom)', 'The dimension description must be unique!'),
                        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '%s (%s)' % (record.name, record.uom)
            vals.append((record.id, name))

        return vals


########### description tab
class LightingProductApplication(models.Model):
    _name = 'lighting.product.application'

    name = fields.Char(string='Application', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The application must be unique!'),
                        ]

class LightingProductFinish(models.Model):
    _name = 'lighting.product.finish'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The finish name must be unique!'),
                        ('code_uniq', 'unique (code)', 'The finish code must be unique!'),
                        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            vals.append((record.id, name))

        return vals

class LightingProductMaterial(models.Model):
    _name = 'lighting.product.material'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The material name must be unique!'),
                        ('code_uniq', 'unique (code)', 'The material code must be unique!'),
                        ]

###### Electrical characteristics tab
class LightingProductProtectionClass(models.Model):
    _name = 'lighting.product.protectionclass'

    name = fields.Char(string='Class', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The protection class must be unique!'),
                        ]

class LightingProductFrequency(models.Model):
    _name = 'lighting.product.frequency'

    name = fields.Char(string='Frequency', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The frequency must be unique!'),
                        ]

class LightingProductDimmable(models.Model):
    _name = 'lighting.product.dimmable'

    name = fields.Char(string='Dimmable', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The dimmable must be unique!'),
                        ]

class LightingProductAuxiliaryEquipment(models.Model):
    _name = 'lighting.product.auxiliaryequipment'

    name = fields.Char(string='Auxiliary equipment', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The auxiliary equipment must be unique!'),
                        ]

class LightingProductAuxiliaryEquipmentModel(models.Model):
    _name = 'lighting.product.auxiliaryequipmentmodel'

    name = fields.Char(string='Auxiliary equipment model', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The auxiliary equipment model must be unique!'),
                        ]

class LightingProductVoltage(models.Model):
    _name = 'lighting.product.voltage'

    name = fields.Char(compute='_compute_name', string='Voltage', required=True)

    voltage1 = fields.Float(string="Voltage 1 (V)", required=True)
    voltage2_check = fields.Boolean(string="Voltage 2 check")
    voltage2 = fields.Float(string="Voltage 2 (V)", required=False, default=None)
    current_type = fields.Selection(selection=[('AC', 'Alternating'), ('DC', 'Direct')], string="Current type", required=True)


    _sql_constraints = [('voltage_uniq', 'unique (voltage1, voltage2, voltage2_check, current_type)',
                            'It already exists another voltage with the same parameters'),
                        ]

    @api.depends('voltage1', 'voltage2', 'voltage2_check','current_type')
    def _compute_name(self):
        # TODO voltage que si no te decimals no posi .0
        for record in self:
            voltage_l = []
            if record.voltage1!=0:
                voltage_l.append('%i' % record.voltage1)

            if record.voltage2_check and record.voltage2!=0:
                voltage_l.append('-%i' % record.voltage2)

            if voltage_l:
                voltage_l.append('V')

            if record.current_type:
                voltage_l.append(' %s' % record.current_type)

            if voltage_l:
                record.name = ''.join(voltage_l)

    @api.onchange('voltage2_check')
    def _onchange_voltage2_check(self):
        if not self.voltage2_check:
            self.voltage2 = False


    @api.constrains('voltage1', 'voltage2', 'voltage2_check')
    def _check_voltages(self):
        self.ensure_one()
        if self.voltage1==0:
            raise ValidationError("Voltage 1 cannot be 0")

        if self.voltage2_check and self.voltage2==0:
            raise ValidationError("Voltage 2 cannot be 0")

class LightingProductSensor(models.Model):
    _name = 'lighting.product.sensor'

    name = fields.Char(string='Sensor', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The sensor must be unique!'),
                        ]

###########  Lighting characteristics tab
class LightingProductLedBrand(models.Model):
    _name = 'lighting.product.ledbrand'

    name = fields.Char(string='LED brand', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The LED brand must be unique!'),
                        ]

###########  Physical characteristics tab
class LightingProductDimension(models.Model):
    _name = 'lighting.product.dimension'

    _rec_name = 'type_id'

    type_id = fields.Many2one(comodel_name='lighting.dimension.type', ondelete='restrict', string='Dimension', required=True)
    value = fields.Float(string='Value', required=True)
    sequence = fields.Integer(required=True, default=1,
        help="The sequence field is used to define order in which the dimension lines are sorted")

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='restrict', string='Product')

class LightingProductRecessDimension(models.Model):
    _name = 'lighting.product.recessdimension'

    _rec_name = 'type_id'

    type_id = fields.Many2one(comodel_name='lighting.dimension.type', ondelete='restrict', string='Recess dimension', required=True)
    value = fields.Float(string='Value', required=True)
    sequence = fields.Integer(required=True, default=1,
        help="The sequence field is used to define order in which the recess dimension lines are sorted")

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='restrict', string='Product')

class LightingProductEcorraeCategory(models.Model):
    _name = 'lighting.product.ecorraecategory'

    name = fields.Char(string='Description', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The ecorrae category description must be unique!'),
                        ]

class LightingProductEcorrae2Category(models.Model):
    _name = 'lighting.product.ecorrae2category'

    name = fields.Char(string='Description', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The ecorrae2 category description must be unique!'),
                        ]

class LightingProductPhotobiologicalRiskGroup(models.Model):
    _name = 'lighting.product.photobiologicalriskgroup'

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

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")

    relevance = fields.Selection([('main', 'Main'), ('aux', 'Auxiliary')], string='Relevance', required=True, default='main')
    num = fields.Integer(string='Number of sources', default=1)
    lampholder_id =  fields.Many2one(comodel_name='lighting.product.source.lampholder', ondelete='restrict', string='Lampholder')
    lampholder_marketing_id = fields.Many2one(comodel_name='lighting.product.source.lampholder', ondelete='restrict',
                                    string='Marketing lampholder')

    line_ids = fields.One2many(comodel_name='lighting.product.source.line', inverse_name='source_id', string='Lines')

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='restrict', string='Product')


    ## computed fields
    line_display = fields.Char(compute='_compute_line_display', string='Sources')

    @api.depends('line_ids')
    def _compute_line_display(self):
        for rec in self:
            res = []
            for l in rec.line_ids.sorted(lambda x: x.sequence):
                #res0 = [l.type_id.code]
                #if l.wattage_display:
                #    res0.append(l.wattage_display)

                res.append(l.type_id.code)

            if res != []:
                rec.line_display = "/".join(res)


class LightingProductSourceLine(models.Model):
    _name = 'lighting.product.source.line'

    _rec_name = 'type_id'

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")

    type_id = fields.Many2one(comodel_name='lighting.product.source.type', ondelete='restrict', string='Type', required=True)
    wattage = fields.Integer(string='Wattage (W)')
    is_max_wattage = fields.Boolean(string='Max. Wattage (W)')

    luminous_flux1 = fields.Integer(string='Luminous flux 1 (Lm)')
    luminous_flux2 = fields.Integer(string='Luminous flux 2 (Lm)')
    color_temperature = fields.Integer(string='Color temperature (K)')
    special_spectrum = fields.Selection([('blue' ,'Blue'), ('meat', 'Meat'), ('fashion', 'Moda'),
                                         ('multifood', 'Multi Food'), ('bread', 'Bread'),
                                         ('fish', 'Fish'), ('vegetable', 'Vegetable')
                                         ], string='Special spectrum')

    efficiency_ids = fields.Many2many(comodel_name='lighting.energyefficiency',
                                  relation='lighting_product_source_energyefficiency_rel',
                                  string='Energy efficiency')

    is_lamp_included = fields.Boolean(string='Lamp included?')
    lamp_included_efficiency_ids = fields.Many2many(comodel_name='lighting.energyefficiency',
                                  relation='lighting_product_source_lampenergyefficiency_rel',
                                  string='Lamp included efficiency')

    wattage_marketing_ids = fields.One2many(comodel_name='lighting.product.source.line.marketingwattage', inverse_name='source_line_id', string='Marketing wattages')

    source_id = fields.Many2one(comodel_name='lighting.product.source', ondelete='restrict', string='Source')


    ## computed fields
    wattage_display = fields.Char(compute='_compute_wattage_display', string='Wattage (W)')

    @api.depends('wattage', 'is_max_wattage')
    def _compute_wattage_display(self):
        for rec in self:
            res = []
            if rec.wattage:
                res.append(float2text(rec.wattage))

                if rec.is_max_wattage:
                    res.append(_('max.'))

                if res != []:
                    rec.wattage_display = " ".join(res)

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


    wattage_marketing_display = fields.Char(compute='_compute_wattage_marketing_display', string='Marketing wattages (W)')

    @api.depends('wattage_marketing_ids')
    def _compute_wattage_marketing_display(self):
        for rec in self:
            res = [float2text(x.wattage) for x in rec.wattage_marketing_ids.sorted(lambda x: x.wattage)]

            if res != []:
                rec.wattage_marketing_display = "-".join(res)

class LightingProductSourceLampholder(models.Model):
    _name = 'lighting.product.source.lampholder'
    _rec_name = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The lampholder name must be unique!'),
                        ('code_uniq', 'unique (code)', 'The lampholder code must be unique!'),
                        ]

class LightingProductSourceType(models.Model):
    _name = 'lighting.product.source.type'
    _rec_name = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The source type description must be unique!'),
                        ('code_uniq', 'unique (code)', 'The source type code must be unique!'),
                        ]

class LightingProductSourceLineMarketingWattage(models.Model):
    _name = 'lighting.product.source.line.marketingwattage'
    _rec_name = 'wattage'

    wattage = fields.Float(string='Marketing wattage (W)', required=True)

    source_line_id = fields.Many2one(comodel_name='lighting.product.source.line', ondelete='cascade', string='Source line')

    _sql_constraints = [('wattage_line_uniq', 'unique (source_line_id, wattage)', 'There are duplicated marketing wattages on a source line!'),
                    ]

    @api.constrains('wattage')
    def _check_wattage(self):
        for rec in self:
            if rec.wattage == 0:
                raise ValidationError("The marketing wattage on a source line, if defined, cannot be 0")


########### beams tab
class LightingProductBeam(models.Model):
    _name = 'lighting.product.beam'

    _rec_name = 'relevance'

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")

    relevance = fields.Selection([('main', 'Main'), ('aux', 'Auxiliary')], string='Relevance', required=True, default='main')
    num = fields.Integer(string='Number of beams', default=1)

    photometric_distribution_ids = fields.Many2many(comodel_name='lighting.product.beam.photodistribution',
                                                    relation='lighting_product_beam_photodistribution_rel',
                                                    string='Photometric distributions')

    dimension_ids = fields.One2many(comodel_name='lighting.product.beam.dimension', inverse_name='beam_id', string='Dimensions')

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='restrict', string='Product')


    ## computed fields
    dimensions_display = fields.Char(compute='_compute_dimensions_display', string='Dimensions')

    @api.depends('dimension_ids')
    def _compute_dimensions_display(self):
        for rec in self:
            res = []
            for dimension in rec.dimension_ids.sorted(lambda x: x.sequence):
                res.append('%s: %f' % (dimension.type_id.name, dimension.value))

            rec.dimensions_display = ', '.join(res)


class LightingProductBeamPhotometricDistribution(models.Model):
    _name = 'lighting.product.beam.photodistribution'

    name = fields.Char(string='Description', translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The photometric distribution name must be unique!'),
                        ]

class LightingProductBeamDimension(models.Model):
    _name = 'lighting.product.beam.dimension'

    type_id = fields.Many2one(comodel_name='lighting.dimension.type', ondelete='restrict', string='Dimension', required=True)
    value = fields.Float(string='Value', required=True)
    sequence = fields.Integer(required=True, default=1,
        help="The sequence field is used to define order in which the dimension lines are sorted")

    beam_id = fields.Many2one(comodel_name='lighting.product.beam', ondelete='restrict', string='Beam')

########### attachment button
class LightingAttachment(models.Model):
    _name = 'lighting.attachment'

    name = fields.Char(string='Description', translate=True)
    type_id = fields.Many2one(comodel_name='lighting.attachment.type', ondelete='restrict', required=True, string='Type')

    datas = fields.Binary(string="Document", attachment=True)
    datas_fname = fields.Char(string='Filename')

    lang_id = fields.Many2one(comodel_name='lighting.language', ondelete='restrict', string='Language')

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='restrict', string='Product')

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '%s (%s)' % (record.datas_fname, record.type_id.name)
            vals.append((record.id, name))

        return vals


class LightingAttachmentType(models.Model):
    _name = 'lighting.attachment.type'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The attachment type description must be unique!'),
                        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            if record.name:
                name = '%s (%s)' % (record.name, record.code)
            else:
                name = record.code

            vals.append((record.id, name))

        return vals


class LightingLanguage(models.Model):
    _name = 'lighting.language'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Language', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The language must be unique!'),
                        ('code_uniq', 'unique (code)', 'The language code must be unique!'),
                        ]

########### logistics tab
class LightingAssembler(models.Model):
    _name = 'lighting.assembler'

    name = fields.Char(string='Asssembler', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The assembler must be unique!'),
                        ]

class LightingProductSupplier(models.Model):
    _name = 'lighting.product.supplier'

    _rec_name = 'supplier_id'

    sequence = fields.Integer(required=True, default=1,
                              help="The sequence field is used to define the priority of suppliers")
    supplier_id = fields.Many2one(comodel_name='lighting.supplier', ondelete='restrict', string='Supplier', required=True)
    reference = fields.Char(string="Supplier reference")

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='restrict', string='Product')


class LightingSupplier(models.Model):
    _name = 'lighting.supplier'

    name = fields.Char(string='Description', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The supplier description must be unique!'),
                        ]

########### marketing tab
class LightingProductState(models.Model):
    _name = 'lighting.product.state'

    name = fields.Char(string='State', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The state description must be unique!'),
                        ]


"""
gnx_compliance_statement = fields.Many2many(comodel_name='ir.attachment', string="GNX compliance statement")
eu_manufacturer_declaration = fields.Many2many(comodel_name='ir.attachment', string="EU Manufacturer Declaration")
emc = fields.Many2many(comodel_name='ir.attachment', string="EMC")
lvd = fields.Many2many(comodel_name='ir.attachment', string="LVD")
rohs = fields.Many2many(comodel_name='ir.attachment', string="RoHS")
others_test_reports = fields.Many2many(comodel_name='ir.attachment', string="Other's test reports")

installation_instructions = fields.Many2many(comodel_name='ir.attachment', string="Installation instructions")
assembly_instructions = fields.Many2many(comodel_name='ir.attachment', string="Assembly instructions")
"""



'''
@api.depends('category_id.name', 'name')
def _compute_full_name(self):
    # Important: value must be stored in environment of group, not group1!
    for group, group1 in pycompat.izip(self, self.sudo()):
        if group1.category_id:
            group.full_name = '%s / %s' % (group1.category_id.name, group1.name)
        else:
            group.full_name = group1.name

def _search_full_name(self, operator, operand):
    lst = True
    if isinstance(operand, bool):
        domains = [[('name', operator, operand)], [('category_id.name', operator, operand)]]
        if operator in expression.NEGATIVE_TERM_OPERATORS == (not operand):
            return expression.AND(domains)
        else:
            return expression.OR(domains)
    if isinstance(operand, pycompat.string_types):
        lst = False
        operand = [operand]
    where = []
    for group in operand:
        values = [v for v in group.split('/') if v]
        group_name = values.pop().strip()
        category_name = values and '/'.join(values).strip() or group_name
        group_domain = [('name', operator, lst and [group_name] or group_name)]
        category_domain = [('category_id.name', operator, lst and [category_name] or category_name)]
        if operator in expression.NEGATIVE_TERM_OPERATORS and not values:
            category_domain = expression.OR([category_domain, [('category_id', '=', False)]])
        if (operator in expression.NEGATIVE_TERM_OPERATORS) == (not values):
            sub_where = expression.AND([group_domain, category_domain])
        else:
            sub_where = expression.OR([group_domain, category_domain])
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            where = expression.AND([where, sub_where])
        else:
            where = expression.OR([where, sub_where])
    return where

@api.model
def search(self, args, offset=0, limit=None, order=None, count=False):
    # add explicit ordering if search is sorted on full_name
    if order and order.startswith('full_name'):
        groups = super(Groups, self).search(args)
        groups = groups.sorted('full_name', reverse=order.endswith('DESC'))
        groups = groups[offset:offset+limit] if limit else groups[offset:]
        return len(groups) if count else groups.ids
    return super(Groups, self).search(args, offset=offset, limit=limit, order=order, count=count)
'''

'''
@api.model
def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    res = super(LightingProduct, self).fields_view_get(
        view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

    if res['type'] == 'form' and res['name'] == 'product.form':
        doc = etree.XML(res['arch'])

        for node in doc.xpath("//field[@name='product_id']"):
            if self._context['type'] in ('in_invoice', 'in_refund'):
                # Hack to fix the stable version 8.0 -> saas-12
                # purchase_ok will be moved from purchase to product in master #13271
                if 'purchase_ok' in self.env['product.template']._fields:
                    node.set('domain', "[('purchase_ok', '=', True)]")
            else:
                node.set('domain', "[('sale_ok', '=', True)]")
        res['arch'] = etree.tostring(doc, encoding='unicode')


    return res
'''

'''
@api.model
def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    def get_view_id(xid, name):
        try:
            return self.env.ref('account.' + xid)
        except ValueError:
            view = self.env['ir.ui.view'].search([('name', '=', name)], limit=1)
            if not view:
                return False
            return view.id

    context = self._context
    if context.get('active_model') == 'res.partner' and context.get('active_ids'):
        partner = self.env['res.partner'].browse(context['active_ids'])[0]
        if not view_type:
            view_id = get_view_id('invoice_tree', 'account.invoice.tree')
            view_type = 'tree'
        elif view_type == 'form':
            if partner.supplier and not partner.customer:
                view_id = get_view_id('invoice_supplier_form', 'account.invoice.supplier.form').id
            elif partner.customer and not partner.supplier:
                view_id = get_view_id('invoice_form', 'account.invoice.form').id
    return super(AccountInvoice, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                       submenu=submenu)

@api.model
def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    res = super(AccountInvoiceLine, self).fields_view_get(
        view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    if self._context.get('type'):
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='product_id']"):
            if self._context['type'] in ('in_invoice', 'in_refund'):
                # Hack to fix the stable version 8.0 -> saas-12
                # purchase_ok will be moved from purchase to product in master #13271
                if 'purchase_ok' in self.env['product.template']._fields:
                    node.set('domain', "[('purchase_ok', '=', True)]")
            else:
                node.set('domain', "[('sale_ok', '=', True)]")
        res['arch'] = etree.tostring(doc, encoding='unicode')
    return res

'''

'''
    efficiency_display = fields.Char(compute='_compute_efficiency_display', string='Energy efficiency')
    @api.depends('efficiency_ids')
    def _compute_efficiency_display(self):
        for rec in self:
            res = [x.name for x in rec.efficiency_ids.sorted(lambda x: x.sequence)]

            if res != []:
                rec.efficiency_display = "/".join(res)

'''

'''
    @api.multi
    def _compute_attachment_count(self):
        attachment_data = self.env['lighting.attachment'].read_group([('product_id', 'in', self.ids)], ['product_id'],
                                                            ['product_id'])
        mapped_data = dict([(attachment['product_id'][0], attachment['product_id_count']) for attachment in attachment_data])
        for record in self:
            record.attachment_count = mapped_data.get(record.id, 0)
            '''