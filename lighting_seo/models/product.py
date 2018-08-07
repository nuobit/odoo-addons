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