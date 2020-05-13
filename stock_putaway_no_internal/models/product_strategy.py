# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class PutAwayStrategy(models.Model):
    _inherit = 'product.putaway'

    exclude_internal_operations = fields.Boolean(string='Exclude internal operations',
                                                 default=False)
