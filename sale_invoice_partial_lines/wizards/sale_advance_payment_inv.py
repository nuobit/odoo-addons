# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    only_selected_lines = fields.Boolean(
        string="Only selected lines",
        default=False,
        help="When set, the invoice will include only the order lines flagged "
        "as 'Selected'. After the invoice is created, the flag is reset on "
        "every line that was just invoiced.",
    )

    def _create_invoices(self, sale_orders):
        self.ensure_one()
        if not self.only_selected_lines or self.advance_payment_method != "delivered":
            return super()._create_invoices(sale_orders)
        selected_invoiceable_lines = self.env["sale.order.line"]
        selective_sale_orders = sale_orders.with_context(only_selected_lines=True)
        for order in selective_sale_orders:
            selected_invoiceable_lines |= order._get_invoiceable_lines(
                final=self.deduct_down_payments
            ).filtered(
                lambda line: line.selected
                and not line.display_type
                and not line.is_downpayment
            )
        if not selected_invoiceable_lines:
            raise UserError(
                _(
                    "No selected order lines are ready to invoice. Tick the "
                    "'Selected' checkbox on invoiceable lines before creating "
                    "the invoice."
                )
            )
        res = super(
            SaleAdvancePaymentInv,
            self.with_context(only_selected_lines=True),
        )._create_invoices(selective_sale_orders)
        selected_invoiceable_lines.write({"selected": False})
        return res
