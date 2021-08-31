# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        return super(
            StockMove,
            self.with_context(stock_picking_type_code=self.picking_type_id.code),
        )._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    @api.onchange("product_id", "product_uom_id", "move_id")
    def _onchange_product_id(self):
        picking_code = self.move_id.picking_code
        return super(
            StockMoveLine, self.with_context(stock_picking_type_code=picking_code)
        )._onchange_product_id()
