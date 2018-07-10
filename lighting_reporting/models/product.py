# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProduct(models.Model):
    _inherit = 'lighting.product'

    @api.multi
    def print_product(self):
        return self.env.ref('lighting_reporting.action_report_product').report_action(self)