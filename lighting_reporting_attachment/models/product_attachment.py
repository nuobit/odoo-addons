# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _


class LightingAttachment(models.Model):
    _inherit = 'lighting.attachment'

    use_as_product_datasheet = fields.Boolean(string="Use as a product datasheet", default=False)
