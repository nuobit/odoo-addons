# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class DocumentPageArchiveReason(models.TransientModel):
    _name = "document.page.archive.reason"
    _description = "Archive document pages with reason"

    document_page_ids = fields.Many2many(
        "document.page",
        required=True,
        string="Document Pages",
    )
    reason = fields.Text(
        required=True,
        string="Reason",
        help="Reason for archiving. Will be logged in the chatter of each "
        "affected document for traceability.",
    )

    def action_confirm(self):
        self.ensure_one()
        pages = self.document_page_ids
        pages.with_context(
            archive_reason_provided=True,
            tracking_disable=True,
        ).write({"active": False})
        body = (
            _("<strong>Document archived.</strong><br/><strong>Reason:</strong> %s")
            % self.reason
        )
        for doc in pages:
            doc.message_post(body=body, subtype_xmlid="mail.mt_note")
        return {"type": "ir.actions.act_window_close"}
