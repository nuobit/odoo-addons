from odoo import api, fields, models, _

class VlProduct(models.Model):
    _name = 'vl.product'

    name = fields.Char(string='Description', translate=True)  #required=True
    reference = fields.Char(string='Reference', required=True, index=True, copy=False)
    ean = fields.Char(string='EAN', required=True, index=True, copy=False)
    category_id = fields.Many2one(comodel_name='vl.category', ondelete='restrict', string='Category')
    catalog_ids = fields.Many2many(comodel_name='vl.catalog', relation='vl_product_vl_catalog_rel', )
    type_id = fields.Many2one(comodel_name='vl.type', ondelete='restrict', string='Type')
    environment = fields.Selection(selection=[('indoor', _('Indoor')), ('outdoor', _('Outdoor')), ('underwater', _('Underwater'))
                                ], string='Environment', required=True)
    application_id = fields.Many2one(comodel_name='vl.application', ondelete='restrict', string='Application')
    finish_id = fields.Many2one(comodel_name='vl.finish', ondelete='restrict', string='Finish')
    body_material_id = fields.Many2one(comodel_name='vl.material', ondelete='restrict', string='Body material')
    diffusor_material_id = fields.Many2one(comodel_name='vl.material', ondelete='restrict', string='Diffusor material')
    frame_material_id = fields.Many2one(comodel_name='vl.material', ondelete='restrict', string='Frame material')
    reflector_material_id = fields.Many2one(comodel_name='vl.material', ondelete='restrict', string='Reflector material')
    blade_material_id = fields.Many2one(comodel_name='vl.material', ondelete='restrict', string='Blade material')

    ip_check = fields.Boolean(string="IP")
    ip = fields.Integer(string="IP")

    ip2_check = fields.Boolean(string="IP2")
    ip2 = fields.Integer(string="IP2")

    ik_check = fields.Boolean(string="IK")
    ik = fields.Selection(
        selection=[("%02d" % x, "%02d" % x) for x in range(11)], string='IK')

    static_pressure_kg = fields.Float(string="Static pressure (kg)")
    dynamic_pressure_kg = fields.Float(string="Dynamic pressure (kg)")
    corrosion_resistance = fields.Boolean(string="Corrosion resistance")

    attachment_ids = fields.One2many(comodel_name='vl.attachment', inverse_name='product_id', string='Attachments')

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


class VlCatalog(models.Model):
    _name = 'vl.catalog'

    name = fields.Char(string='Catalog', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The name of catalog must be unique!'),
                        ]

class VlCategory(models.Model):
    _name = 'vl.category'

    name = fields.Char(string='Category', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The name of category must be unique!'),
                        ]

class VlType(models.Model):
    _name = 'vl.type'

    name = fields.Char(string='Type', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The type must be unique!'),
                        ]

class VlApplication(models.Model):
    _name = 'vl.application'

    name = fields.Char(string='Application', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The application must be unique!'),
                        ]

class VlFinish(models.Model):
    _name = 'vl.finish'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The finish name must be unique!'),
                        ('code_uniq', 'unique (code)', 'The finish code must be unique!'),
                        ]

class VlMaterial(models.Model):
    _name = 'vl.material'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The material name must be unique!'),
                        ('code_uniq', 'unique (code)', 'The material code must be unique!'),
                        ]

class VlAttachment(models.Model):
    _name = 'vl.attachment'

    name = fields.Char(string='Description', translate=True)
    type_id = fields.Many2one(comodel_name='vl.attachment.type', ondelete='restrict', required=True, string='Type')

    datas = fields.Binary(string="Document", attachment=True)
    datas_fname = fields.Char(string='Filename')

    product_id = fields.Many2one(comodel_name='vl.product', ondelete='restrict', string='Product')

class VlAttachmentType(models.Model):
    _name = 'vl.attachment.type'

    name = fields.Char(string='Description', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The attachment type description must be unique!'),
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



