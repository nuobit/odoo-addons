# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"

    @api.constrains("removal_date")
    def _check_name(self):
        for rec in self:
            if rec.gs1_generated:
                raise ValidationError(
                    _(
                        "If the lot has a GS1 generated,"
                        " the removal date cannot be modified"
                    )
                )
