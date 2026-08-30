# Copyright NuoBiT Solutions SL - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends("order_line.price_total", "date_order")
    def _amount_all(self):
        for rec in self:
            return super(
                PurchaseOrder,
                rec.with_context(
                    **self.env["account.tax"].prorate_context(
                        rec, rec.date_order, rec.company_id
                    )
                ),
            )._amount_all()


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends("product_qty", "price_unit", "taxes_id", "order_id.date_order")
    def _compute_amount(self):
        for rec in self:
            return super(
                PurchaseOrderLine,
                rec.with_context(
                    **self.env["account.tax"].prorate_context(
                        rec.order_id, rec.order_id.date_order, rec.order_id.company_id
                    )
                ),
            )._compute_amount()
