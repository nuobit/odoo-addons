# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import odoo.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    service_time = fields.Float(
        string='Service Time',
        digits=dp.get_precision('Product UoM'),
        help='Time to complete this service.',
    )

    @api.multi
    @api.constrains('service_time')
    def _check_service_time(self):
        for record in self:
            if record.service_time <= 0:
                raise ValidationError(_(
                    'Time must be greater than 0.'
                ))
