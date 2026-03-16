# Copyright NuoBiT Solutions SL - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _trigger_assign(self):
        if self.env.context.get("flowable_skip_trigger_assign"):
            return
        return super()._trigger_assign()

    def write(self, vals):
        for rec in self:
            production = rec.raw_material_production_id
            if not production.picking_type_id.flowable_operation:
                continue
            new_state = vals.get("state")
            if not new_state:
                continue
            # Block location when MO raw materials are fully reserved
            if new_state == "assigned":
                if (
                    vals.get("move_line_ids", rec.move_line_ids)
                    and production.location_dest_id.flowable_storage
                    and not production.location_dest_id.flowable_blocked
                ):
                    production.location_dest_id.flowable_production_id = production
            # Unblock location when MO raw materials are done or cancelled
            elif new_state in ("cancel", "done"):
                if production.location_dest_id.flowable_production_id == production:
                    production.location_dest_id.flowable_production_id = False
        return super().write(vals)
