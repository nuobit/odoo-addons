# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingPortalProduct(models.Model):
    _inherit = 'lighting.portal.product'

    @api.multi
    def print_product(self):
        return self.env.ref('lighting_portal_product_report.action_report_portal_product').report_action(self)