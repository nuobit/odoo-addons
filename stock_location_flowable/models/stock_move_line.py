# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    raw_production_blocked = fields.Boolean(
        related="move_id.raw_material_production_id.production_blocked"
    )

    @api.constrains("state")
    def _check_flowable_location_blocked(self):
        for rec in self:
            if rec.state not in ("draft", "cancel"):
                locations_to_check = self.env["stock.location"]
                if (
                    rec.location_dest_id.flowable_storage
                    and rec.location_dest_id.flowable_blocked
                ):
                    locations_to_check |= rec.location_dest_id
                if (
                    rec.location_id.flowable_storage
                    and rec.location_id.flowable_blocked
                ):
                    locations_to_check |= rec.location_id
                for location in locations_to_check:
                    if rec.state == "done":
                        production = rec.move_id.production_id
                    else:
                        production = rec.move_id.raw_material_production_id
                    if production and location.flowable_production_id != production:
                        raise ValidationError(
                            _(
                                "The location %s is blocked. Probably you need to"
                                " review the pending manufacturing orders related"
                                " to this location"
                            )
                            % location.name
                        )
