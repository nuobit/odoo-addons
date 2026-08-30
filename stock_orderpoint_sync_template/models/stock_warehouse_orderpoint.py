# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockWarehouseOrderpoint(models.Model):
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
