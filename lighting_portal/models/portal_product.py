# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class LightingPortalProduct(models.Model):
    _name = 'lighting.portal.product'
    _rec_name = 'reference'
    _order = 'reference'

    reference = fields.Char(string='Reference', required=True)
    description = fields.Char(string='Description')
    catalog = fields.Char(string='Catalog')
    qty_available = fields.Integer(string='Quantity available')

    atp_ids = fields.One2many(comodel_name='lighting.portal.product.atp',
                              inverse_name='portal_product_id', string='ATP quantity')
    qty_ordered = fields.Integer(string='Quantity ordered', compute="_compute_qty_ordered")
    @api.depends('atp_ids.qty_ordered')
    def _compute_qty_ordered(self):
        for rec in self:
            rec.qty_ordered = sum(atp.qty_ordered for atp in rec.atp_ids)

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='set null',
                                 string='Product',
                                 groups='lighting_portal.portal_group_manager')

    _sql_constraints = [('reference', 'unique (reference)', 'The reference must be unique!'),
                        ]


class LightingPortalProductATP(models.Model):
    _name = 'lighting.portal.product.atp'
    _order = 'ship_date'

    qty_ordered = fields.Integer(string='Quantity ordered', required=True)
    ship_date = fields.Date(string='Ship date', required=True)

    portal_product_id = fields.Many2one(comodel_name='lighting.portal.product', ondelete='restrict',
                                        string='Product')


    _sql_constraints = [('product_date', 'unique (portal_product_id, ship_date)', _('Only one ship date is allowed for a product')),
                        ]