# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

## main model
class LightingPortalProduct(models.Model):
    _name = 'lighting.portal.product'
    _rec_name = 'reference'
    _order = 'reference'

    reference = fields.Char(string='Reference', required=True)
    description = fields.Char(string='Description')
    catalog = fields.Char(string='Catalog')
    qty_available = fields.Integer(string='Quantity available')

    _sql_constraints = [('reference', 'unique (reference)', 'The reference must be unique!'),
                        ]

    @api.multi
    def print_product(self):
        return self.env.ref('lighting_portal.action_report_portal_product').report_action(self)