# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class StockMoveLocationWizard(models.TransientModel):
    _inherit = "wiz.stock.move.location"

    def _get_default_picking_type(self):
        company_id = self.env.context.get("company_id") or self.env.company.id
        picking_type = self.env["stock.picking.type"].search(
            [
                ("code", "=", "internal"),
                ("use_in_location_moves", "=", True),
                ("company_id", "=", company_id),
            ],
        )
        if not picking_type:
            raise ValidationError(
                _(
                    "You must first set a default picking type marked as "
                    "'Use in location moves'"
                )
            )
        return picking_type

    picking_type_id = fields.Many2one(
        default=lambda self: self._get_default_picking_type(),
    )
