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
    date = fields.Date(string='Date', required=True)

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
                    if l.color_temperature_ids:
                        line.append(l.color_temperature_display)
                    if l.luminous_flux_display:
                        line.append("%slm" % l.luminous_flux_display)
                    if l.is_led and l.cri_min:
                        line.append("%iCRI" % l.cri_min)

                if l.wattage_display:
                    line.append("(%s)" % l.wattage_display)

                res.append(' '.join(line))

            if res != []:
                rec.line_display = " / ".join(res)

    ## aux display functions
    def get_source_type(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            s = []
            if src.lampholder_id:
                s.append(src.lampholder_id.display_name)

            src_t = src.line_ids.get_source_type()
            if src_t:
                s.append('/'.join(src_t))

            s_l = None
            if s:
                s_l = ' '.join(s)
            res.append(s_l)

        if not any(res):
            return None
        return res

    def get_color_temperature(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            src_k = src.line_ids.get_color_temperature()
            k_l = None
            if src_k:
                k_l = ','.join(src_k)
            res.append(k_l)

        if not any(res):
            return None
        return res

    def get_luminous_flux(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            src_k = src.line_ids.get_luminous_flux()
            k_l = None
            if src_k:
                kn_l = []
                if src.num > 1:
                    kn_l.append('%ix' % src.num)
                kn_l.append('/'.join(src_k))
                k_l = ' '.join(kn_l)
            res.append(k_l)

        if not any(res):
            return None
        return res

    def get_wattage(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            src_k = src.line_ids.get_wattage()
            if src_k:
                kn_l = []
                if src.num > 1:
                    kn_l.append('%ix' % src.num)
                kn_l.append(src_k)
                src_k = ' '.join(kn_l)
            res.append(src_k)

        if not any(res):
            return None
        return res


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

    luminous_flux1 = fields.Integer(string='Luminous flux 1 (lm)')
    luminous_flux2 = fields.Integer(string='Luminous flux 2 (lm)')

    color_temperature_ids = fields.Many2many(string='Color temperature (K)',
                                             comodel_name='lighting.product.color.temperature',
                                             relation='lighting_product_source_line_color_temperature_rel',
                                             column1='source_line_id', column2='color_temperature_id')
    is_color_temperature_tunable = fields.Boolean(string='Tunable', default=False)

    @api.onchange('color_temperature_ids', 'is_color_temperature_tunable')
    def _onchange_is_color_temperature_ids_tunable(self):
        if len(self.color_temperature_ids) > 2:
            if self.is_color_temperature_tunable:
                color_temps_ord = self.color_temperature_ids.sorted(lambda x: x.value)
                self.color_temperature_ids = [
                    (6, False, (color_temps_ord[0] | color_temps_ord[-1]).mapped('id'))]
        elif len(self.color_temperature_ids) < 2:
            if self.is_color_temperature_tunable:
                self.is_color_temperature_tunable = False

    color_temperature_display = fields.Char(string='Color temperature (K)',
                                            compute='_compute_color_temperature_display')

    def _compute_color_temperature_display(self):
        for rec in self:
            if rec.color_temperature_ids:
                rec.color_temperature_display = (rec.is_color_temperature_tunable and '-' or '/') \
                    .join(['%iK' % x.value for x in
                           rec.color_temperature_ids.sorted(lambda y: y.value)])

    cri_min = fields.Integer(string='CRI', help='Minimum color rendering index', track_visibility='onchange')

    is_led = fields.Boolean(related='type_id.is_led')
    color_consistency = fields.Float(string='Color consistency (SDCM)')
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

    luminous_flux_display = fields.Char(compute='_compute_luminous_flux_display', string='Luminous flux (lm)')

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

    @api.multi
    @api.constrains('type_id')
    def _check_integrated_vs_lamp_included(self):
        for rec in self:
            if rec.type_id.is_integrated:
                rec.is_lamp_included = False

    @api.multi
    @api.constrains('color_temperature_ids', 'is_color_temperature_tunable')
    def _check_color_temperature_ids_tunable(self):
        if self.is_color_temperature_tunable and self.color_temperature_ids and \
                len(self.color_temperature_ids) != 2:
            raise ValidationError(_("A tunable source must have exactly 2 color temperatures"))

    # aux display fucnitons
    def get_source_type(self):
        res = self.sorted(lambda x: x.sequence) \
            .mapped('type_id.display_name')
        if not res:
            return None
        return res

    def get_color_temperature(self):
        res = self.filtered(lambda x: x.color_temperature_ids) \
            .sorted(lambda x: x.sequence) \
            .mapped('color_temperature_display')
        if not res:
            return None
        return res

    def get_cri(self):
        res = self.sorted(lambda x: x.sequence) \
            .mapped('cri_min')
        if not res:
            return None
        return res

    def get_luminous_flux(self):
        res = []
        for line in self.sorted(lambda x: x.sequence):
            lm_l = ['%ilm' % x for x in
                    filter(lambda x: x, [line.luminous_flux1, line.luminous_flux2])]
            if lm_l:
                res.append('-'.join(lm_l))

        if not res:
            return None
        return res

    def get_wattage(self):
        w_d = {}
        for rec in self:
            if rec.wattage:
                if rec.wattage_magnitude not in w_d:
                    w_d[rec.wattage_magnitude] = []
                w_d[rec.wattage_magnitude].append(rec.wattage)

        if not w_d:
            return None

        wattage_magnitude_option = dict(
            self.fields_get(['wattage_magnitude'], ['selection'])
                .get('wattage_magnitude').get('selection'))

        w_l = []
        for wm, wv_l in w_d.items():
            ws = wattage_magnitude_option.get(wm)
            w_l.append('%g%s' % (max(wv_l), ws))

        return '%s %s' % ('/'.join(w_l), _('max.'))


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
            rec.dimensions_display = rec.dimension_ids.get_display()

    # aux display functions
    def get_beam_photometric_distribution(self):
        res = []
        for rec in self.sorted(lambda x: x.sequence):
            if rec.photometric_distribution_ids:
                res.append(', '.join([x.display_name for x in rec.photometric_distribution_ids]))

        if not any(res):
            return None
        return res

    def get_beam(self):
        res = []
        for rec in self.sorted(lambda x: x.sequence):
            bm = []
            if rec.num > 1:
                bm.append('%ix' % rec.num)

            if rec.photometric_distribution_ids:
                bm.append(rec.get_beam_photometric_distribution()[0])

            dimension_display = rec.dimension_ids.get_display()
            if dimension_display:
                bm.append(dimension_display)

            if bm:
                res.append(' '.join(bm))

        if not any(res):
            return None
        return res

    def get_beam_angle(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            angl = []
            for d in src.dimension_ids.sorted(lambda x: x.sequence):
                if d.value and d.type_id.uom == 'º':
                    angl.append('%g%s' % (d.value, d.type_id.uom))
            ang_v = None
            if angl:
                ang_v = '/'.join(angl)
            res.append(ang_v)

        if not any(res):
            return None
        return res


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
    _inherit = 'lighting.product.dimension.abstract'

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
