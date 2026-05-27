# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models, tools
from odoo.exceptions import UserError


class DocumentPageArchiveReason(models.TransientModel):
    _name = "document.page.archive.reason"
    _description = "Archive document pages with reason"

    document_page_ids = fields.Many2many(
        comodel_name="document.page",
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
        pages = self.document_page_ids.with_context(mail_notrack=True)
        reason = (self.reason or "").strip()
        if not reason:
            raise UserError(_("Archive reason is required."))
        pages._check_can_archive_with_reason()
        pages.archive_reason = reason
        body = _("Document archived.<br/>Reason: %s") % tools.html_escape(reason)
        for doc in pages:
            doc.message_post(body=body, subtype_xmlid="mail.mt_note")
        pages.with_context(archive_reason_validated=True).action_archive()
        return {"type": "ir.actions.act_window_close"}
