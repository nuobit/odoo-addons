# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductSource(models.Model):
    _inherit = 'lighting.product.source'

    def get_energy_efficiency(self):
        return self.mapped('line_ids') \
            .mapped('efficiency_ids') \
            .sorted(lambda x: x.sequence)
