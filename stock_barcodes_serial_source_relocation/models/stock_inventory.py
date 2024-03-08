# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    def _get_move_values(self, qty, location_id, location_dest_id, out):
        values = super()._get_move_values(qty, location_id, location_dest_id, out)
        origin = self.env.context.get("relocation_origin", False)
        if origin:
            values["origin"] = origin
            values["move_line_ids"][0][2]["origin"] = origin
        return values
