# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# Eric Antones <eatones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    is_lot_required = fields.Boolean(compute="_compute_is_lot_required")

    @api.depends("product_id", "product_id.tracking")
    def _compute_is_lot_required(self):
        for rec in self:
            rec.is_lot_required = rec.product_id.tracking != "none"
