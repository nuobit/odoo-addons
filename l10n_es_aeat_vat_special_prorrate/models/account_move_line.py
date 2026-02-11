# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    prorate_year = fields.Integer(compute="_compute_prorate_year")

    @api.depends("move_id.date", "move_id.line_ids.tax_ids.prorate")
    def _compute_prorate_year(self):
        for line in self:
            move = line.move_id
            has_prorate = bool(move.line_ids.tax_ids.filtered("prorate"))
            line.prorate_year = move.date.year if has_prorate and move.date else 0
