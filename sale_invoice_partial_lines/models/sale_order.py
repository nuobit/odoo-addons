# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    selected_lines_count = fields.Integer(
        string="Selected lines",
        compute="_compute_selected_lines",
        help="Number of selected order lines (sections and notes excluded).",
    )
    selected_lines_amount = fields.Monetary(
        string="Subtotal of selected lines",
        compute="_compute_selected_lines",
        currency_field="currency_id",
        help="Sum of the untaxed subtotal of the selected order lines.",
    )

    @api.depends(
        "order_line.selected",
        "order_line.price_subtotal",
        "order_line.display_type",
    )
    def _compute_selected_lines(self):
        for order in self:
            selected = order.order_line.filtered(
                lambda line: line.selected and not line.display_type
            )
            order.selected_lines_count = len(selected)
            order.selected_lines_amount = sum(selected.mapped("price_subtotal"))

    def _get_invoiceable_lines(self, final=False):
        invoiceable_lines = super()._get_invoiceable_lines(final=final)
        if not self.env.context.get("only_selected_lines"):
            return invoiceable_lines

        # Keep the result from super() as the source of truth for what is
        # invoiceable, then only narrow regular lines to the selected ones.
        invoiceable_line_ids = []
        down_payment_line_ids = []
        group_lines = []
        group_has_selected_line = False

        def flush_group():
            nonlocal group_lines, group_has_selected_line
            if group_has_selected_line:
                invoiceable_line_ids.extend(
                    line.id
                    for line in group_lines
                    if line.display_type or line.selected
                )
            group_lines = []
            group_has_selected_line = False

        for line in invoiceable_lines:
            if line.is_downpayment and not line.display_type:
                down_payment_line_ids.append(line.id)
                continue
            if line.display_type == "line_section":
                flush_group()
                group_lines = [line]
                continue
            group_lines.append(line)
            if not line.display_type and line.selected:
                group_has_selected_line = True
        flush_group()

        return self.env["sale.order.line"].browse(
            invoiceable_line_ids + down_payment_line_ids
        )
