# Copyright NuoBiT 2025 - Bijaya Kumal <bkumal@nuobit.com>

from odoo import models
from odoo.tools import float_is_zero


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_order_lines_to_report(self):
        lines = super()._get_order_lines_to_report()
        return lines.filtered(
            lambda l: not float_is_zero(
                l.product_uom_qty, precision_rounding=l.product_uom.rounding
            )
        )
