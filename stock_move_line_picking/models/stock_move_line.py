from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    picking_id = fields.Many2one(
        related="move_id.picking_id", store=True, readonly=False
    )
