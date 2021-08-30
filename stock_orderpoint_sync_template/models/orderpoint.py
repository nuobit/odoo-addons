from odoo import fields, models


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    sync_template_line_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint.sync.template.line",
        string="Template line",
        readonly=True,
        ondelete="restrict",
    )
    sync_template_id = fields.Many2one(
        related="sync_template_line_id.sync_template_id",
        string="Template",
        readonly=True,
        store=True,
    )
