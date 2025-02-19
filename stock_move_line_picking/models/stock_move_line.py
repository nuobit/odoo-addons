from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    additional_field = fields.Char()
