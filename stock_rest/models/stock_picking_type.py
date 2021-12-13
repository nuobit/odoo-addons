# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    use_in_rest_operations = fields.Boolean(string="Use in REST operations")

    @api.constrains("use_in_rest_operations")
    def _check_use_in_rest_operations(self):
        for rec in self:
            other = self.search(
                [
                    ("id", "!=", rec.id),
                    ("warehouse_id.company_id", "=", rec.warehouse_id.company_id.id),
                    ("use_in_rest_operations", "=", True),
                ]
            )
            if other:
                raise ValidationError(
                    _(
                        "Only one picking type can be used in REST operations for the same company"
                    )
                )
