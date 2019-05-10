# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields, _


class LightingProductFamily(models.Model):
    _inherit = 'lighting.product.family'

    no_templates = fields.Boolean(string='No templates',
                                  help="Enabled if this family is NOT allowed to "
                                       "contain templates (products with variants)")
