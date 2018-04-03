from odoo import api, fields, models, _
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree

#### auxiliary functions
def float2text(f, decs=2):
    if f == int(f):
        return '%i' % int(f)
    else:
        return ("{0:.%if}" % decs).format(f)

COLOR_SELECTION = [ ('meat', 'Meat'), ('fashion', 'Fashion'),
                    ('multifood', 'Multi Food'), ('bread', 'Bread'),
                    ('fish', 'Fish'), ('vegetable', 'Vegetable'),
                    ('blue', _('Blue')), ('orange', _('Orange')),
                    ('green', _('Green')), ('red', _('Red')),
                    ('purple', _('Purple')), ('pink', _('Pink')),
                ]

## main model
class LightingProduct(models.Model):
    _name = 'lighting.product'
    _rec_name = 'reference'
    _order = 'reference'

    # Common data
    reference = fields.Char(string='Reference', required=True, index=True)
    description = fields.Char(string='Description', translate=True)  #required=True
    ean = fields.Char(string='EAN', required=True, index=True)
    family_ids = fields.Many2many(comodel_name='lighting.product.family',
                                  relation='lighting_product_family_rel', string='Families')
    catalog_ids = fields.Many2many(comodel_name='lighting.catalog', relation='lighting_product_catalog_rel', string='Catalogs')
    type_id = fields.Many2one(comodel_name='lighting.product.type', ondelete='restrict', string='Type')

    _sql_constraints = [ ('reference_uniq', 'unique (reference)', 'The reference must be unique!'),
                         ('ean_uniq', 'unique (ean)', 'The EAN must be unique!')
        ]

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
                    rec.total_wattage += line.wattage

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

    color_consistency = fields.Float(string='Color consistency')

    color = fields.Selection(selection=COLOR_SELECTION, string='Color')

    led_driver_ids = fields.One2many(comodel_name='lighting.product.leddriver', inverse_name='product_id', string='LED drivers')

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
        for rec in self:
            rec.source_count = sum(rec.source_ids.mapped('num'))

    # Beams tab
    beam_ids = fields.One2many(comodel_name='lighting.product.beam', inverse_name='product_id', string='Beams')

    beam_count = fields.Integer(compute='_compute_beam_count', string='Total beams')

    @api.depends('beam_ids')
    def _compute_beam_count(self):
        for rec in self:
            rec.beam_count = sum(rec.beam_ids.mapped('num'))

    # Attachment tab
    attachment_ids = fields.One2many(comodel_name='lighting.attachment', inverse_name='product_id', string='Attachments')
    attachment_count = fields.Integer(compute='_compute_attachment_count', string='Attachment(s)')

    @api.depends('attachment_ids')
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

    ########### external data tab
    external_data_available = fields.Boolean(compute='_compute_external_data_available', readonly=True)

    ext_itemname = fields.Char(string='Item name', readonly=True)
    ext_frgnname = fields.Char(string='Foreign name', readonly=True)
    ext_codebars = fields.Char(string='Code bar', readonly=True)
    ext_onhand = fields.Integer(string='On hand', readonly=True)
    ext_avgprice = fields.Float(string='Average price', readonly=True)
    ext_stockvalue = fields.Float(string='Stock value', readonly=True)
    ext_lastpurdat = fields.Date(string='Last purchase date', readonly=True)
    ext_sheight1 = fields.Float(string='S Height 1', readonly=True)
    ext_swidth1 = fields.Float(string='S Width 1', readonly=True)
    ext_slength1 = fields.Float(string='S Length 1', readonly=True)
    ext_svolume = fields.Float(string='S Volume', readonly=True)
    ext_sweight1 = fields.Float(string='S Weight 1', readonly=True)

    def _compute_external_data_available(self):
        for rec in self:
            try:
                from hdbcli import dbapi
            except ImportError:
                rec.external_data_available = False
                return

            if self.env['lighting.settings'].sudo().search_count([]) == 0:
                rec.external_data_available = False
                return

            rec.external_data_available = True

    def get_external_data(self):
        ext_fields = ["ItemCode", "ItemName", "FrgnName", "CodeBars",
                      "OnHand", "AvgPrice", "StockValue", "LastPurDat",
                      "SHeight1", "SWidth1", "SLength1", "SVolume", "SWeight1"]

        settings = self.env['lighting.settings'].sudo().search([]).sorted(lambda x: x.sequence)

        from hdbcli import dbapi

        conn = dbapi.connect(settings['host'],
                             settings['port'],
                             settings['username'],
                             settings['password'])

        cursor = conn.cursor()
        stmnt = """SELECT %s
                   FROM %s.OITM p 
                   WHERE p."ItemCode" = ?""" % (', '.join(['p."%s"' % x for x in ext_fields]),
                                                settings['schema'])
        cursor.execute(stmnt, self.reference)
        header = [x[0] for x in cursor.description]
        result = cursor.fetchone()
        if result is not None:
            result_d = dict(zip(header, result))
            #TODO deal with more than one occurrence

            for field in ext_fields:
                setattr(self, 'ext_%s' % field.lower(), result_d[field])

        cursor.close()
        conn.close()

    def dupOne2many(self, default, pfield, cfields):
        l = []
        for p in getattr(self, pfield):
            d = {}
            for c in cfields:
                b = p[c]
                if c.endswith('_id'):
                    b = b.id
                d.update({c: b})
            l.append((0, False, d))

        if l != []:
            default.update({pfield: l})

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {},
                       reference=_('%s (copy)') % self.reference,
                       ean=_('%s (copy)') % self.ean,
                       )

        self.dupOne2many(default, 'led_driver_ids', ['reference', 'brand_id'])
        self.dupOne2many(default, 'dimension_ids', ['type_id', 'value'])
        self.dupOne2many(default, 'recess_dimension_ids', ['type_id', 'value'])
        self.dupOne2many(default, 'fan_wattage_ids', ['wattage'])
        self.dupOne2many(default, 'supplier_ids', ['supplier_id', 'reference'])

        return super(LightingProduct, self).copy(default)

######### common data
class LightingCatalog(models.Model):
    _name = 'lighting.catalog'
    _order = 'name'

    name = fields.Char(string='Catalog', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The name of catalog must be unique!'),
                        ]

class LightingProductFamily(models.Model):
    _name = 'lighting.product.family'
    _order = 'name'

    name = fields.Char(string='Family', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The family must be unique!'),
                        ]

class LightingProductType(models.Model):
    _name = 'lighting.product.type'
    _order = 'name'

    name = fields.Char(string='Type', required=True, translate=True)
    is_accessory = fields.Boolean(string='Is accessory')

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
class LightingProductApplication(models.Model):
    _name = 'lighting.product.application'
    _order = 'name'

    name = fields.Char(string='Application', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The application must be unique!'),
                        ]

class LightingProductFinish(models.Model):
    _name = 'lighting.product.finish'
    _order = 'code'

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
    _order = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The material name must be unique!'),
                        ('code_uniq', 'unique (code)', 'The material code must be unique!'),
                        ]

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

class LightingProductAuxiliaryEquipment(models.Model):
    _name = 'lighting.product.auxiliaryequipment'
    _order = 'name'

    name = fields.Char(string='Auxiliary equipment', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The auxiliary equipment must be unique!'),
                        ]

class LightingProductAuxiliaryEquipmentModel(models.Model):
    _name = 'lighting.product.auxiliaryequipmentmodel'
    _order = 'name'

    name = fields.Char(string='Auxiliary equipment model', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The auxiliary equipment model must be unique!'),
                        ]

class LightingProductVoltage(models.Model):
    _name = 'lighting.product.voltage'
    _order = 'name'

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
    _order = 'name'

    name = fields.Char(string='Sensor', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The sensor must be unique!'),
                        ]

###########  Lighting characteristics tab

class LightingProductLedDriver(models.Model):
    _name = 'lighting.product.leddriver'
    _rec_name = 'reference'

    reference = fields.Char(string='Reference')
    brand_id = fields.Many2one(comodel_name='lighting.product.ledbrand', ondelete='restrict', string='Brand')

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')

    _sql_constraints = [('leddriver_uniq', 'unique (product_id, reference, brand_id)', 'The LED brand must be unique!'),
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
    is_max_wattage = fields.Boolean(string='Max. Wattage')
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
    special_spectrum = fields.Selection(COLOR_SELECTION, string='Special spectrum')

    efficiency_ids = fields.Many2many(comodel_name='lighting.energyefficiency',
                                  relation='lighting_product_source_energyefficiency_rel',
                                  string='Energy efficiency')

    is_lamp_included = fields.Boolean(string='Lamp included?')
    lamp_included_efficiency_ids = fields.Many2many(comodel_name='lighting.energyefficiency',
                                  relation='lighting_product_source_lampenergyefficiency_rel',
                                  string='Lamp included efficiency')

    wattage_marketing_ids = fields.One2many(comodel_name='lighting.product.source.line.marketingwattage', inverse_name='source_line_id', string='Marketing wattages')

    source_id = fields.Many2one(comodel_name='lighting.product.source', ondelete='cascade', string='Source')

    ## computed fields
    wattage_display = fields.Char(compute='_compute_wattage_display', string='Wattage (W)')

    @api.depends('wattage', 'is_max_wattage', 'wattage_magnitude')
    def _compute_wattage_display(self):
        wattage_magnitude_option = dict(
            self.fields_get(['wattage_magnitude'], ['selection']).get('wattage_magnitude').get('selection'))

        for rec in self:
            res = []
            if rec.wattage > 0:
                wattage_str = float2text(rec.wattage)
                if rec.wattage_magnitude:
                    wattage_str += wattage_magnitude_option.get(rec.wattage_magnitude)
                res.append(wattage_str)

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
    _order = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The lampholder name must be unique!'),
                        ('code_uniq', 'unique (code)', 'The lampholder code must be unique!'),
                        ]

class LightingProductSourceType(models.Model):
    _name = 'lighting.product.source.type'
    _rec_name = 'code'
    _order = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', translate=True)
    is_integrated = fields.Boolean(string='Integrated')

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
    _order = 'sequence'

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")

    num = fields.Integer(string='Number of beams', required=True, default=1)

    photometric_distribution_ids = fields.Many2many(comodel_name='lighting.product.beam.photodistribution',
                                                    relation='lighting_product_beam_photodistribution_rel',
                                                    string='Photometric distributions')

    dimension_ids = fields.One2many(comodel_name='lighting.product.beam.dimension', inverse_name='beam_id', string='Dimensions')

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

class LightingProductBeamDimension(models.Model):
    _name = 'lighting.product.beam.dimension'
    _order = 'sequence'

    type_id = fields.Many2one(comodel_name='lighting.dimension.type', ondelete='restrict', string='Dimension', required=True)
    value = fields.Float(string='Value', required=True)
    sequence = fields.Integer(required=True, default=1,
        help="The sequence field is used to define order in which the dimension lines are sorted")

    beam_id = fields.Many2one(comodel_name='lighting.product.beam', ondelete='cascade', string='Beam')

########### attachment button
class LightingAttachment(models.Model):
    _name = 'lighting.attachment'
    _order = 'type_id'

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
            name = '%s (%s)' % (record.datas_fname, record.type_id.display_name)
            vals.append((record.id, name))

        return vals

class LightingAttachmentType(models.Model):
    _name = 'lighting.attachment.type'
    _order = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', translate=True)

    _sql_constraints = [('name_uniq', 'unique (code)', 'The attachment type description must be unique!'),
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

########### Configuration
class LightingSettings(models.Model):
    _name = 'lighting.settings'

    sequence = fields.Integer(required=True, default=1,
                              help="The sequence field is used to define the priority of settngs")
    host = fields.Char(string='Host', required=True)
    port = fields.Integer(string='Port', required=True)
    schema = fields.Char(string='Schema', required=True)
    username = fields.Char(string='Username', required=True)
    password = fields.Char(string='Password', required=True)


    _sql_constraints = [('settings_uniq', 'unique (host, port, username)', 'The host, port, username must be unique!'),
                        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '%s@%s:%s' % (record.host, record.port, record.username)

            vals.append((record.id, name))

        return vals