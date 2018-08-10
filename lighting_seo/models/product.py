# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models, api


class LightingProduct(models.Model):
    _inherit = 'lighting.product'

    seo_title = fields.Char(string='Meta title', translate=True)
    seo_url = fields.Char(string='URL')
    seo_description = fields.Char(string='Meta description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword', relation='lighting_product_seo_keyword_rel',
                                       column1='product_id', column2='keyword_id', string='Keywords')


class LightingProductFamily(models.Model):
    _inherit = 'lighting.product.family'

    seo_title = fields.Char(string='Meta title', translate=True)
    seo_url = fields.Char(string='URL')
    seo_description = fields.Text(string='Meta description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword',
                                       relation='lighting_product_family_seo_keyword_rel',
                                       column1='family_id', column2='keyword_id', string='Keywords')

    meta_title_length = fields.Integer(string='Meta title length', compute='_compute_lengths', readonly=True)
    meta_description_length = fields.Integer(string='Meta description length', compute='_compute_lengths',
                                             readonly=True)

    @api.depends('seo_title', 'seo_description')
    def _compute_lengths(self):
        for rec in self:
            if rec.seo_title:
                rec.meta_title_length = len(rec.seo_title)
                rec.meta_description_length = len(rec.seo_description)


class LightingProductType(models.Model):
    _inherit = 'lighting.product.type'

    seo_title = fields.Char(string='Meta title', translate=True)
    seo_url = fields.Char(string='URL')
    seo_description = fields.Char(string='Meta description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword',
                                       relation='lighting_product_type_seo_keyword_rel',
                                       column1='type_id', column2='keyword_id', string='Keywords')


class LightingProductApplication(models.Model):
    _inherit = 'lighting.product.application'

    seo_title = fields.Char(string='Meta title', translate=True)
    seo_url = fields.Char(string='URL')
    seo_description = fields.Char(string='Meta description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword',
                                       relation='lighting_product_application_seo_keyword_rel',
                                       column1='application_id', column2='keyword_id', string='Keywords')


class LightingCatalog(models.Model):
    _inherit = 'lighting.catalog'

    seo_title = fields.Char(string='Meta title', translate=True)
    seo_url = fields.Char(string='URL')
    seo_description = fields.Char(string='Meta description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword', relation='lighting_catalog_seo_keyword_rel',
                                       column1='catalog_id', column2='keyword_id', string='Keywords')