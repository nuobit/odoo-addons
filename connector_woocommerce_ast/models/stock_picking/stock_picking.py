# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    woocommerce_stock_picking_state = fields.Selection(
        selection_add=[
            ("delivered", "Delivered"),
        ],
    )

    def _get_woocommerce_stock_picking_state(self):
        self.ensure_one()
        woocommerce_stock_picking_state = super()._get_woocommerce_stock_picking_state()
        if (
            woocommerce_stock_picking_state == "done"
            and self.delivery_state == "shipping_recorded_in_carrier"
        ):
            woocommerce_stock_picking_state = "delivered"
        return woocommerce_stock_picking_state

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if "carrier_tracking_ref" in vals or "carrier_id" in vals:
                self.env["sale.order"]._event(
                    "on_compute_woocommerce_order_state"
                ).notify(rec.sale_id, fields={"woocommerce_ast_fields"})
        return res
