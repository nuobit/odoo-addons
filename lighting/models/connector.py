# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree

## main model
class LightingConnectorProduct(models.Model):
    _name = 'lighting.connector.product'
    _rec_name = 'reference'
    _order = 'reference'

    reference = fields.Char(string='Reference', readonly=True)

    description = fields.Char(string='Description', readonly=True)

    catalog = fields.Char(string='Catalog', readonly=True)

    qty_available = fields.Integer(string='Quantity available', readonly=True)

    last_update = fields.Datetime(string='Last update', readonly=True)

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='restrict',
                                 string='Product', readonly=True, groups='lighting.connector_group_manager')

    _sql_constraints = [('reference', 'unique (reference)', 'The reference must be unique!'),
                        ]

    def update(self):
        self.ensure_one()
        tdelta = fields.datetime.now() - fields.Datetime.from_string(self.last_update)
        if tdelta.seconds < 300:
            raise UserError(_("Only one update is allowed every 5 minutes"))

        self.env['lighting.connector.product.sync'].synchronize(reference=self.reference)

    @api.multi
    def print_product(self):
        return self.env.ref('lighting.action_report_connector_product').report_action(self)
