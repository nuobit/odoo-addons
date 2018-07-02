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
    quantity = fields.Integer(string='Quantity')

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='set null',
                                 string='Product',
                                 groups='lighting_portal.portal_group_manager')

    _sql_constraints = [('reference', 'unique (reference)', 'The reference must be unique!'),
                        ]