# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


def prorate_context(order):
    return {
        "date": order.date_order,
        "company_id": order.company_id.id,
    }


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends("date_order")
    def _amount_all(self):
        for rec in self:
            super(
                PurchaseOrder, rec.with_context(prorate=prorate_context(rec))
            )._amount_all()


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _compute_amount(self):
        for rec in self:
            super(
                PurchaseOrderLine,
                rec.with_context(prorate=prorate_context(rec.order_id)),
            )._compute_amount()
