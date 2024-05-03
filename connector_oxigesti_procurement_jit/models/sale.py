# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        if not self.env.context.get("skip_reserved_quantity", False):
            super()._action_launch_stock_rule(
                previous_product_uom_qty=previous_product_uom_qty
            )
