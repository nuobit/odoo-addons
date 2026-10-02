# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .document_page_history_recipient import SENT_STATES


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
    # facts of the version, the same for every reader
    distribution_sent_count = fields.Integer(
        compute="_compute_distribution_sent_count",
        compute_sudo=True,
    )
    distribution_summary = fields.Char(
        compute="_compute_distribution_summary",
        compute_sudo=True,
    )

    @api.depends("recipient_ids")
    def _compute_distribution_count(self):
        for history in self:
            history.distribution_count = len(history.recipient_ids)

    @api.depends("recipient_ids.state")
    def _compute_distribution_sent_count(self):
        for history in self:
            history.distribution_sent_count = len(
                history.recipient_ids.filtered(
                    lambda recipient: recipient.state in SENT_STATES
                )
            )

    @api.depends("distribution_count", "distribution_sent_count")
    def _compute_distribution_summary(self):
        for history in self:
            if history.distribution_count:
                history.distribution_summary = "%s/%s" % (
                    history.distribution_sent_count,
                    history.distribution_count,
                )
            else:
                history.distribution_summary = False
