# Copyright NuoBiT Solutions SL - Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class RepairLine(models.Model):
    _inherit = "stock.move"

    @api.onchange("repair_line_type")
    def onchange_operation_type(self):
        if (
            self.repair_line_type == "add"
            and self.move_lines_count == 0
            and self.product_id
        ):
            self.move_line_ids = [
                (
                    0,
                    0,
                    {
                        "product_id": self.product_id.id,
                        "location_id": self.repair_id.location_id.id,
                        "quantity": self.product_uom_qty,
                    },
                )
            ]
