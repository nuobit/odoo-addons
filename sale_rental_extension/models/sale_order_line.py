# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    rental_qty = fields.Float(
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "sent": [("readonly", False)],
            "sale": [("readonly", False)],
        },
    )

    @api.onchange("product_id", "rental_qty")
    def rental_product_id_change(self):
        res = super().rental_product_id_change()
        if (
            self.product_id.rented_product_id
            and self.rental_type == "new_rental"
            and not self.rental_qty
        ):
            self.rental_qty = 1
        return res

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        if self._context.get("skip_procurement"):
            return True
        return super()._action_launch_stock_rule(
            previous_product_uom_qty=previous_product_uom_qty
        )

    def write(self, values):
        if "rental_qty" in values:
            rental_lines = self.filtered(
                lambda l: l.state in ("sale", "done")
                and l.rental_type == "new_rental"
                and l.product_id.rented_product_id
            )
            for line in rental_lines:
                rental = self.env["sale.rental"].search(
                    [("start_order_line_id", "=", line.id)], limit=1
                )
                if rental and rental.out_move_id.state == "done":
                    raise UserError(
                        _(
                            "Cannot change rental quantity after pickup "
                            "for product '%s'.",
                            line.product_id.display_name,
                        )
                    )
        else:
            rental_lines = self.env["sale.order.line"]

        res = super().write(values)

        for line in rental_lines:
            new_qty = line.rental_qty * line.number_of_days
            if line.product_uom_qty != new_qty:
                line.with_context(skip_procurement=True).write(
                    {"product_uom_qty": new_qty}
                )
            rental = self.env["sale.rental"].search(
                [("start_order_line_id", "=", line.id)], limit=1
            )
            if rental:
                moves_to_update = self.env["stock.move"]
                if rental.out_move_id and rental.out_move_id.state not in (
                    "done",
                    "cancel",
                ):
                    moves_to_update |= rental.out_move_id
                if rental.in_move_id and rental.in_move_id.state not in (
                    "done",
                    "cancel",
                ):
                    moves_to_update |= rental.in_move_id
                if moves_to_update:
                    moves_to_update.move_line_ids.write({"qty_done": 0})
                    moves_to_update.write({"product_uom_qty": line.rental_qty})

        return res
