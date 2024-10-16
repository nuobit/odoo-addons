# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    woocommerce_stock_picking_state = fields.Selection(
        compute="_compute_woocommerce_stock_picking_state",
        selection=[
            ("processing", "Processing"),
            ("done", "Done"),
            ("cancel", "Cancel"),
        ],
    )

    def _get_woocommerce_stock_picking_state(self):
        self.ensure_one()
        if self.state == "done":
            woocommerce_stock_picking_state = "done"
        elif self.state == "cancel":
            woocommerce_stock_picking_state = "cancel"
        else:
            woocommerce_stock_picking_state = "processing"
        return woocommerce_stock_picking_state

    @api.depends("state")
    def _compute_woocommerce_stock_picking_state(self):
        for rec in self:
            if rec.sale_id.is_woocommerce:
                woocommerce_stock_picking_state = (
                    rec._get_woocommerce_stock_picking_state()
                )
                rec.woocommerce_stock_picking_state = woocommerce_stock_picking_state
            else:
                rec.woocommerce_stock_picking_state = False
