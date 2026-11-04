# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_round


class StockMove(models.Model):
    _inherit = "stock.move"

    is_dynamic_receipt = fields.Boolean(
        string="Receipt in a Dynamic Unit",
        compute="_compute_is_dynamic_receipt",
    )
    purchase_uom_qty = fields.Integer(
        string="Purchase Units Received",
        compute="_compute_purchase_uom_qty",
        inverse="_inverse_purchase_uom_qty",
        store=True,
        readonly=False,
        copy=False,
        recursive=True,
        help="How many units of the purchase line this receipt line brings, when "
        "they are bought in a unit whose quantity is known only on receipt: the "
        "labels share the quantity received among them. It proposes the units "
        "still to come.",
    )
    purchase_uom_qty_entered = fields.Boolean(
        string="Purchase Units Entered",
        copy=False,
        help="The purchase units received of this receipt line were entered, so "
        "it no longer proposes them.",
    )

    _sql_constraints = [
        (
            "purchase_uom_qty_not_negative",
            "CHECK(purchase_uom_qty >= 0)",
            "The purchase units received cannot be negative.",
        ),
    ]

    @api.depends(
        "purchase_line_id.product_uom.dynamic_ratio",
        "location_dest_id.usage",
        "origin_returned_move_id",
    )
    def _compute_is_dynamic_receipt(self):
        # goods bought in a dynamic unit and received, not sent back
        for move in self:
            move.is_dynamic_receipt = (
                move.purchase_line_id.product_uom.dynamic_ratio
                and not move._is_purchase_return()
            )

    @api.depends(
        "is_dynamic_receipt",
        "purchase_uom_qty_entered",
        "purchase_line_id.product_qty",
        "purchase_line_id.move_ids.state",
        "purchase_line_id.move_ids.purchase_uom_qty",
    )
    def _compute_purchase_uom_qty(self):
        # a receipt in a dynamic unit proposes the units still to come, a part
        # of a unit counted as one, until they are entered or it is done: then
        # it keeps its units. Other moves do not use it
        for move in self:
            if (
                move.is_dynamic_receipt
                and move.state != "done"
                and not move.purchase_uom_qty_entered
            ):
                line = move.purchase_line_id
                received = line.move_ids.filtered(
                    lambda m: m.is_dynamic_receipt and m.state == "done"
                )
                to_come = line.product_qty - sum(received.mapped("purchase_uom_qty"))
                move.purchase_uom_qty = max(
                    int(float_round(to_come, precision_digits=0, rounding_method="UP")),
                    0,
                )

    def _inverse_purchase_uom_qty(self):
        # the units entered stay, whatever changes on the purchase line after
        self.purchase_uom_qty_entered = True

    def _action_done(self, cancel_backorder=False):
        # a receipt keeps its units once it is done, and its proposal is
        # computed only when read: compute it while the receipt is still open
        self.filtered("is_dynamic_receipt").flush_recordset(["purchase_uom_qty"])
        return super()._action_done(cancel_backorder=cancel_backorder)
