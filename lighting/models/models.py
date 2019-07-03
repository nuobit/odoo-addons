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
