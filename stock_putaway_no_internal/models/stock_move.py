# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _apply_putaway_strategy(self):
        for picking_type, move_lines in self.grouped(
            lambda line: line.move_id.picking_type_id or line.picking_id.picking_type_id
        ).items():
            super(
                StockMoveLine,
                move_lines.with_context(stock_picking_type_code=picking_type.code),
            )._apply_putaway_strategy()
        return None

    @api.onchange("result_package_id", "product_id", "product_uom_id", "quantity")
    def _onchange_putaway_location(self):
        picking_type = self.move_id.picking_type_id or self.picking_id.picking_type_id
        return super(
            StockMoveLine,
            self.with_context(stock_picking_type_code=picking_type.code),
        )._onchange_putaway_location()
