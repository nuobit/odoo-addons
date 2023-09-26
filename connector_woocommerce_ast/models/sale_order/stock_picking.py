# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if "carrier_tracking_ref" in vals or "carrier_id" in vals:
                self.env["sale.order"]._event(
                    "on_compute_woocommerce_order_state"
                ).notify(rec.sale_id, fields={"woocommerce_ast_fields"})
        return res
