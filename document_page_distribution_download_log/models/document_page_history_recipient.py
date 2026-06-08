# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class DocumentPageHistoryRecipient(models.Model):
    _inherit = "document.page.history.recipient"

    download_ids = fields.One2many(
        "document.page.history.recipient.download",
        "recipient_id",
        string="Downloads",
    )
    downloaded = fields.Boolean(
        compute="_compute_download_info",
        store=True,
    )
    download_count = fields.Integer(
        compute="_compute_download_info",
        store=True,
    )
    first_download_date = fields.Datetime(
        compute="_compute_download_info",
        store=True,
    )
    last_download_date = fields.Datetime(
        compute="_compute_download_info",
        store=True,
    )

    @api.depends("download_ids", "download_ids.download_date")
    def _compute_download_info(self):
        for recipient in self:
            downloads = recipient.download_ids.sorted("download_date")
            recipient.download_count = len(downloads)
            recipient.downloaded = bool(downloads)
            recipient.first_download_date = downloads[:1].download_date or False
            recipient.last_download_date = downloads[-1:].download_date or False

    def action_open_downloads(self):
        self.ensure_one()
        return {
            "name": _("Downloads"),
            "type": "ir.actions.act_window",
            "res_model": "document.page.history.recipient.download",
            "view_mode": "tree,form",
            "domain": [("recipient_id", "=", self.id)],
            "target": "new",
        }
