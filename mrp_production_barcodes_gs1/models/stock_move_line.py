# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.depends("move_id.product_uom_qty")
    def _compute_quantity(self):
        res = super()._compute_quantity()
        for record in self:
            if record.move_id.production_id:
                move_lines = record.move_id.move_line_ids
                if move_lines:
                    record.quantity = record.move_id.product_uom_qty / len(move_lines)
        return res
