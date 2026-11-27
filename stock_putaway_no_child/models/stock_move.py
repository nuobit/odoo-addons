# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        return super(
            StockMove,
            self.with_context(stock_location_dest=self.location_dest_id),
        )._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange("product_id", "product_uom_id", "move_id")
    def _onchange_product_id(self):
        location_dest = self.move_id.location_dest_id
        return super(
            StockMoveLine, self.with_context(stock_location_dest=location_dest)
        )._onchange_product_id()
