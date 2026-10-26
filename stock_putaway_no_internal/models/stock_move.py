# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        return super(
            StockMove,
            self.with_context(stock_picking_type_code=self.picking_type_id.code),
        ).prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)


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
