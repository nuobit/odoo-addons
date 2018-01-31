from odoo import api, fields, models, _

class LightingProduct(models.Model):
    _name = 'lighting.product'
    #_rec_name = 'full_name'
    _rec_name = 'reference'

    name = fields.Char(string='Description', translate=True)  #required=True
    #full_name = fields.Char(compute='_compute_full_name', string='Product Name', search='_search_full_name')
    reference = fields.Char(string='Reference', required=True, index=True, copy=False)
    ean = fields.Char(string='EAN', required=True, index=True, copy=False)
    category_id = fields.Many2one(comodel_name='lighting.category', ondelete='restrict', string='Category')
    catalog_ids = fields.Many2many(comodel_name='lighting.catalog', relation='lighting_product_catalog_rel', string='Catalogs')
    type_id = fields.Many2one(comodel_name='lighting.type', ondelete='restrict', string='Type')
    environment = fields.Selection(selection=[('indoor', _('Indoor')), ('outdoor', _('Outdoor')), ('underwater', _('Underwater'))
                                ], string='Environment', required=True)
    application_id = fields.Many2one(comodel_name='lighting.application', ondelete='restrict', string='Application')
    finish_id = fields.Many2one(comodel_name='lighting.finish', ondelete='restrict', string='Finish')
    body_material_id = fields.Many2one(comodel_name='lighting.material', ondelete='restrict', string='Body material')
    diffusor_material_id = fields.Many2one(comodel_name='lighting.material', ondelete='restrict', string='Diffusor material')
    frame_material_id = fields.Many2one(comodel_name='lighting.material', ondelete='restrict', string='Frame material')
    reflector_material_id = fields.Many2one(comodel_name='lighting.material', ondelete='restrict', string='Reflector material')
    blade_material_id = fields.Many2one(comodel_name='lighting.material', ondelete='restrict', string='Blade material')

    ip_check = fields.Boolean(string="IP")
    ip = fields.Integer(string="IP")

    ip2_check = fields.Boolean(string="IP2")
    ip2 = fields.Integer(string="IP2")

    ik_check = fields.Boolean(string="IK")
    ik = fields.Selection(
        selection=[("%02d" % x, "%02d" % x) for x in range(11)], string='IK')

    static_pressure_kg = fields.Float(string="Static pressure (kg)")
    dynamic_pressure_kg = fields.Float(string="Dynamic pressure (kg)")
    dynamic_pressure_kmh = fields.Float(string="Dynamic pressure (km/h)")
    corrosion_resistance = fields.Boolean(string="Corrosion resistance")
    protection_class = fields.Many2one(comodel_name='lighting.protectionclass', ondelete='restrict', string='Protection class')
    frequency = fields.Many2one(comodel_name='lighting.frequency', ondelete='restrict', string='Frequency')
    dimmable_ids = fields.Many2many(comodel_name='lighting.dimmable', relation='lighting_product_dimmable_rel', string='Dimmable')
    auxiliary_equipment = fields.Many2one(comodel_name='lighting.auxiliaryequipment', ondelete='restrict', string='Auxiliary equipment')

    source_ids = fields.One2many(comodel_name='lighting.source', inverse_name='product_id', string='Sources')

    attachment_ids = fields.One2many(comodel_name='lighting.attachment', inverse_name='product_id', string='Attachments')

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

    technical_comments = fields.Char(string='Technical comments')


    _sql_constraints = [ ('reference_uniq', 'unique (reference)', 'The reference must be unique!'),
                         ('ean_uniq', 'unique (ean)', 'The EAN must be unique!')
        ]

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

class LightingCatalog(models.Model):
    _name = 'lighting.catalog'

    name = fields.Char(string='Catalog', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The name of catalog must be unique!'),
                        ]

class LightingCategory(models.Model):
    _name = 'lighting.category'

    name = fields.Char(string='Category', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The name of category must be unique!'),
                        ]

class LightingType(models.Model):
    _name = 'lighting.type'

    name = fields.Char(string='Type', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The type must be unique!'),
                        ]

class LightingApplication(models.Model):
    _name = 'lighting.application'

    name = fields.Char(string='Application', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The application must be unique!'),
                        ]

class LightingFinish(models.Model):
    _name = 'lighting.finish'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The finish name must be unique!'),
                        ('code_uniq', 'unique (code)', 'The finish code must be unique!'),
                        ]

class LightingMaterial(models.Model):
    _name = 'lighting.material'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The material name must be unique!'),
                        ('code_uniq', 'unique (code)', 'The material code must be unique!'),
                        ]

class LightingProtectionClass(models.Model):
    _name = 'lighting.protectionclass'

    name = fields.Char(string='Class', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The protection class must be unique!'),
                        ]

class LightingFrequency(models.Model):
    _name = 'lighting.frequency'

    name = fields.Char(string='Frequency', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The frequency must be unique!'),
                        ]

class LightingDimmable(models.Model):
    _name = 'lighting.dimmable'

    name = fields.Char(string='Dimmable', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The dimmable must be unique!'),
                        ]


class LightingFrequency(models.Model):
    _name = 'lighting.frequency'

    name = fields.Char(string='Frequency', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The frequency must be unique!'),
                        ]

class LightingAuxiliaryEquipment(models.Model):
    _name = 'lighting.auxiliaryequipment'

    name = fields.Char(string='Auxiliary Equipment', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The auxiliary equipment must be unique!'),
                        ]

class LightingSource(models.Model):
    _name = 'lighting.source'

    _rec_name = 'lamp'

    type = fields.Selection([('main', 'Main'), ('aux', 'Auxiliary')], string='Type')

    lampholder =  fields.Many2one(comodel_name='lighting.lampholder', ondelete='restrict', string='Lampholder')
    lamp = fields.Many2one(comodel_name='lighting.lamp', ondelete='restrict', string='Lamp')
    num = fields.Integer(string='Num')
    wattage = fields.Integer(string='Wattage (W)')
    is_max_wattage = fields.Boolean(string='Max. Wattage (W)')
    luminous_flux1 = fields.Integer(string='Luminous flux 1 (Lm)')
    luminous_flux2 = fields.Integer(string='Luminous flux 2 (Lm)')
    color_temperature = fields.Integer(string='Color temperature (K)')
    special_spectrum = fields.Selection([('blue' ,'Blue'), ('meat', 'Meat'), ('fashion', 'Moda'),
                                         ('multifood', 'Multi Food'), ('bread', 'Bread'),
                                         ('fish', 'Fish'), ('vegetable', 'Vegetable')
                                         ], string='Special spectrum')

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='restrict', string='Product')


class LightingLampholder(models.Model):
    _name = 'lighting.lampholder'
    _rec_name = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The lampholder name must be unique!'),
                        ('code_uniq', 'unique (code)', 'The lampholder code must be unique!'),
                        ]

class LightingLamp(models.Model):
    _name = 'lighting.lamp'
    _rec_name = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The lampholder name must be unique!'),
                        ('code_uniq', 'unique (code)', 'The lampholder code must be unique!'),
                        ]




class LightingAttachment(models.Model):
    _name = 'lighting.attachment'

    name = fields.Char(string='Description', translate=True)
    type_id = fields.Many2one(comodel_name='lighting.attachment.type', ondelete='restrict', required=True, string='Type')

    datas = fields.Binary(string="Document", attachment=True)
    datas_fname = fields.Char(string='Filename')

    lang = fields.Many2one(comodel_name='lighting.language', ondelete='restrict', string='Language')

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='restrict', string='Product')


class LightingAttachmentType(models.Model):
    _name = 'lighting.attachment.type'

    name = fields.Char(string='Description', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The attachment type description must be unique!'),
                        ]

class LightingLanguage(models.Model):
    _name = 'lighting.language'

    name = fields.Char(string='Language', required=True, translate=True)
    code = fields.Char(string='Code', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The language must be unique!'),
                        ('code_uniq', 'unique (code)', 'The language code must be unique!'),
                        ]
"""

from odoo import api, fields, models, _

from lxml import etree

CHILDS = [('sp.product.camshaft', 'Camshaft'), ('sp.product.camshaft.bearing.set', 'Camshaft bearing set')]

class SpProductTemplate(models.Model):
    _inherit = 'product.template'

    sustitute = fields.Char(string='Sustitute')
    note = fields.Char(string='Note')
    is_original = fields.Boolean(string='Original')
    is_original_equipment = fields.Boolean(string='Original equipment')
    is_comercial_equivalent = fields.Boolean(string='Comercial equivalent')
    is_premium = fields.Boolean(string='Premium')

    child_id = fields.Reference(selection=CHILDS, string='Refers to', readonly=True)

    '''
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(SpProductProduct, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            a = 1
            active_id = self.browse(self.env.context['params'].get('id', False))
            if active_id:
                doc = etree.XML(res['arch'])
                for node in doc.xpath("//field[@name='categ_id']"):
                    node.set('string', '%i' % active_id)

                res['arch'] = etree.tostring(doc)


        return res
    '''

class SpProduct(models.AbstractModel):
    _name = 'sp.product'

    product_id = fields.Many2one('product.product', required=True, ondelete='cascade', auto_join=True,
                                 string='Related Product', help='Product-related data')

    @api.model
    def create(self, values):
        res = super(SpProduct, self).create(values)
        res.child_id = res

        return res

    @api.multi
    def unlink(self):
        parent_ids = self.mapped('product_id')
        res = parent_ids.unlink()

        return res



class SpProductCamshaft(SpProduct, models.Model):
    _name = 'sp.product.camshaft'
    _inherits = {'product.product': 'product_id'}

    length = fields.Float(string='Length')
    typ = fields.Char(string='Type')

class SpProductCamshaftBearingSet(SpProduct, models.Model):
    _name = 'sp.product.camshaft.bearing.set'
    _inherits = {'product.product': 'product_id'}

    shaft_diameter_max = fields.Float(string='Shaft diameter max.')
    housing_diameter_min = fields.Float(string='Housing diameter min.')
    wall_thickness_max = fields.Float(string='Wall thickness max.')
    length_max = fields.Float(string='Length max.')
    length_max2 = fields.Float(string='Lenght 2 max.')

"""



