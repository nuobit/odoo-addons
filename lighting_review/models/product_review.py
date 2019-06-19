# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError


class LightingProductReview(models.Model):
    _name = 'lighting.product.review'

    _inherit = ['mail.thread', 'mail.activity.mixin']

    _order = 'package_id,product_id'

    package_id = fields.Many2one(comodel_name='lighting.review.package',
                                 ondelete='restrict', required=True,
                                 track_visibility='onchange')

    reviewed = fields.Boolean(string='Reviewed', track_visibility='onchange')

    date = fields.Datetime(string='Date', readonly=True, track_visibility='onchange')

    comment = fields.Text(string='Comment', track_visibility='onchange')

    product_id = fields.Many2one(comodel_name='lighting.product',
                                 ondelete='cascade', required=True, track_visibility='onchange')

    _sql_constraints = [('uniq1', 'unique (package_id,product_id)',
                         'A package can only be used one time for each product!'),
                        ]

    @api.onchange('reviewed')
    def onchange_reviewed(self):
        if self.reviewed:
            self.date = fields.Datetime.now()
        else:
            self.date = False
