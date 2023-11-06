# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        for rec in self:
            production = rec.raw_material_production_id
            new_state = vals.get("state")
            if (
                production.picking_type_id.flowable_operation
                and production.picking_id
                and production.state == "to_close"
                and new_state != "done"
            ):
                raise UserError(
                    _(
                        "You cannot modify a production with a picking associated."
                        " The mixing is in progress."
                    )
                )
            elif (
                new_state in ("confirmed", "assigned", "partially_available")
                and vals.get("move_line_ids", rec.move_line_ids)
                and production.picking_type_id.flowable_operation
                and production.location_dest_id.flowable_storage
                and not production.location_dest_id.flowable_blocked
            ):
                production.location_dest_id.flowable_production_id = production
            elif production.location_dest_id.flowable_production_id == production:
                if new_state in ("cancel", "done"):
                    production.location_dest_id.flowable_production_id = False
        return super().write(vals)
