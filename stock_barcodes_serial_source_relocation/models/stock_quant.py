# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _get_inventory_move_values(
        self,
        qty,
        location_id,
        location_dest_id,
        package_id=False,
        package_dest_id=False,
    ):
        values = super()._get_inventory_move_values(
            qty, location_id, location_dest_id, package_id, package_dest_id
        )
        origin = self.env.context.get("relocation_origin", False)
        if origin:
            values["origin"] = origin
            values["move_line_ids"][0][2]["origin"] = origin
        return values
