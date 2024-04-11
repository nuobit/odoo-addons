# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.depends("state", "picking_id")
    def _compute_is_initial_demand_editable(self):
        for move in self:
            if move.state == "draft":
                move.is_initial_demand_editable = True
            elif (
                not move.picking_id.is_locked
                and move.state != "done"
                and move.picking_id
            ):
                move.is_initial_demand_editable = True
            else:
                move.is_initial_demand_editable = False
