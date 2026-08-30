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
        picking_code = self.picking_id.picking_type_id.code
        return super(
            StockMoveLine, self.with_context(stock_picking_type_code=picking_code)
        )._apply_putaway_strategy()
