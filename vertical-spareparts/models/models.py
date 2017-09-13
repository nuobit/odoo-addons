from odoo import api, fields, models, _


class SpProductProduct(models.Model):
    _inherit = 'product.product'

    sustitute = fields.Char(string='Sustitute')
    note = fields.Char(string='Note')
    is_original = fields.Boolean(string='Original')
    is_original_equipment = fields.Boolean(string='Original equipment')
    is_comercial_equivalent = fields.Boolean(string='Comercial equivalent')
    is_premium = fields.Boolean(string='Premium')



class SpProductCamshaft(models.Model):
    _name = 'sp.product.camshaft'
    _inherits = {'product.product': 'product_id'}

    product_id = fields.Many2one('product.product', required=True, ondelete='restrict', auto_join=True,
        string='Related Product', help='Product-related data of the Camshaft')

    length = fields.Float(string='Length')
    typ = fields.Char(string='Type')

class SpProductCamshaftBearingSet(models.Model):
    _name = 'sp.product.camshaft.bearing.set'
    _inherits = {'product.product': 'product_id'}

    product_id = fields.Many2one('product.product', required=True, ondelete='restrict', auto_join=True,
        string='Related Product', help='Product-related data of the Camshaft bearing set')

    shaft_diameter_max = fields.Float(string='Shaft diameter max.')
    housing_diameter_min = fields.Float(string='Housing diameter min.')
    wall_thickness_max = fields.Float(string='Wall thickness max.')
    length_max = fields.Float(string='Length max.')
    length_max2 = fields.Float(string='Lenght 2 max.')





