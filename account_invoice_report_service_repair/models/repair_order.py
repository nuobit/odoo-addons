# Copyright 2025 Solutions SL NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Repair(models.Model):
    _inherit = "repair.order"

    date_order = fields.Datetime(
        related="move_id.date", compute_sudo=True, readonly=True
    )

    client_order_ref = fields.Char(compute="_compute_client_order_ref")

    def _compute_client_order_ref(self):
        for order in self:
            order.client_order_ref = False

    service_number = fields.Integer(compute="_compute_service_number")

    def _compute_service_number(self):
        for order in self:
            order.service_number = 0

    date_order_tz = fields.Date(
        string="Order Date TZ", readonly=True, compute="_compute_date_order_tz"
    )

    def _compute_date_order_tz(self):
        for rec in self:
            rec.date_order_tz = fields.Date.context_today(rec, rec.date_order)
