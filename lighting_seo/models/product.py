# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models

class LightingProduct(models.Model):
    _inherit = 'lighting.product'

    seo_description = fields.Char(string='Description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword', relation='lighting_product_seo_keyword_rel',
                                       column1='product_id', column2='keyword_id', string='Keywords')
    url_description = fields.Char(string='URL description')

class LightingProductFamily(models.Model):
    _inherit = 'lighting.product.family'

    seo_description = fields.Char(string='Description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword', relation='lighting_product_family_seo_keyword_rel',
                                       column1='family_id', column2='keyword_id', string='Keywords')
    url_description = fields.Char(string='URL description')

class LightingProductType(models.Model):
    _inherit = 'lighting.product.type'

    seo_description = fields.Char(string='Description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword', relation='lighting_product_type_seo_keyword_rel',
                                       column1='type_id', column2='keyword_id', string='Keywords')
    url_description = fields.Char(string='URL description')

class LightingProductApplication(models.Model):
    _inherit = 'lighting.product.application'

    seo_description = fields.Char(string='Description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword', relation='lighting_product_application_seo_keyword_rel',
                                       column1='application_id', column2='keyword_id', string='Keywords')
    url_description = fields.Char(string='URL description')