# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models

RENTAL_STATUS = [
    ("draft", "Quotation"),
    ("sent", "Quotation Sent"),
    ("pickup", "Reserved"),
    ("return", "Pickedup"),
    ("returned", "Returned"),
    ("cancel", "Cancelled"),
]


class SaleOrder(models.Model):
    _inherit = "sale.order"

    rental_ids = fields.One2many(
        comodel_name="sale.rental",
        inverse_name="start_order_id",
    )
    is_rental_order = fields.Boolean(
        compute="_compute_is_rental_order",
        store=True,
    )
    rental_status = fields.Selection(
        selection=RENTAL_STATUS,
        compute="_compute_rental_status",
        store=True,
    )
    next_action_date = fields.Date(
        compute="_compute_rental_status",
        store=True,
    )
    is_late = fields.Boolean(
        compute="_compute_is_late",
    )
    rental_duration = fields.Integer(
        string="Duration",
        compute="_compute_rental_duration",
    )

    @api.depends("order_line.rental")
    def _compute_is_rental_order(self):
        for order in self:
            order.is_rental_order = any(line.rental for line in order.order_line)

    @api.depends(
        "state",
        "is_rental_order",
        "rental_ids.state",
        "default_start_date",
        "default_end_date",
    )
    def _compute_rental_status(self):
        for order in self:
            order.next_action_date = False
            if not order.is_rental_order:
                order.rental_status = False
            elif order.state in ("draft", "sent", "cancel"):
                order.rental_status = order.state
            elif order.state in ("sale", "done"):
                rental_states = order.rental_ids.mapped("state")
                if any(s == "ordered" for s in rental_states):
                    order.rental_status = "pickup"
                    order.next_action_date = order.default_start_date
                elif any(s in ("out", "sell_progress") for s in rental_states):
                    order.rental_status = "return"
                    order.next_action_date = order.default_end_date
                else:
                    order.rental_status = "returned"

    @api.depends("default_start_date", "default_end_date")
    def _compute_rental_duration(self):
        for order in self:
            if order.default_start_date and order.default_end_date:
                order.rental_duration = (
                    order.default_end_date - order.default_start_date
                ).days + 1
            else:
                order.rental_duration = 0

    @api.depends("next_action_date")
    def _compute_is_late(self):
        today = fields.Date.today()
        for order in self:
            order.is_late = bool(
                order.next_action_date and order.next_action_date < today
            )
