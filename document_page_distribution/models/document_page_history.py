# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DocumentPageHistory(models.Model):
    _inherit = "document.page.history"

    recipient_ids = fields.One2many(
        "document.page.history.recipient",
        "history_id",
        string="Distribution Recipients",
    )
    distribution_count = fields.Integer(
        string="Recipients",
        compute="_compute_distribution_count",
        store=True,
    )

    @api.depends("recipient_ids")
    def _compute_distribution_count(self):
        for history in self:
            history.distribution_count = len(history.recipient_ids)
