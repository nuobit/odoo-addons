# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


def prorate_context(order):
    return (
        fields.Date.to_string(fields.Date.context_today(order, order.date_order)),
        order.company_id.id,
    )


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends("order_line.price_total", "date_order")
    def _amount_all(self):
        for rec in self:
            super(
                PurchaseOrder, rec.with_context(prorate=prorate_context(rec))
            )._amount_all()


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends("product_qty", "price_unit", "taxes_id", "order_id.date_order")
    def _compute_amount(self):
        for rec in self:
            super(
                PurchaseOrderLine,
                rec.with_context(prorate=prorate_context(rec.order_id)),
            )._compute_amount()
