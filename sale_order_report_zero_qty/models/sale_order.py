# Copyright NuoBiT 2025 - Bijaya Kumal <bkumal@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com
from odoo import models
from odoo.tools import float_is_zero


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_order_lines_to_report(self):
        lines = super()._get_order_lines_to_report()
        return lines.filtered(
            lambda l: l.display_type
            or not float_is_zero(
                l.product_uom_qty, precision_rounding=l.product_uom.rounding
            )
        )
