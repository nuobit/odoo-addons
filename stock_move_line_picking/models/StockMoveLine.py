from odoo import models, fields

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    additional_field = fields.Char(string="Additional Field")