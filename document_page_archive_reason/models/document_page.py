# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class DocumentPage(models.Model):
    _inherit = "document.page"

    active = fields.Boolean(tracking=True)

    def _open_archive_reason(self):
        records = self.filtered("active")
        already_archived = self - records
        if already_archived:
            details = "\n".join("- %s" % r.display_name for r in already_archived)
            raise UserError(
                _("Cannot archive document(s) that are already archived:\n%s") % details
            )
        if not records:
            return False
        view = self.env.ref(
            "document_page_archive_reason.document_page_archive_reason_form"
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Archive"),
            "res_model": "document.page.archive.reason",
            "view_mode": "form",
            "view_id": view.id,
            "views": [(view.id, "form")],
            "target": "new",
            "context": {
                "default_document_page_ids": [(6, 0, records.ids)],
                "active_test": False,
            },
        }

    def action_archive(self):
        if self.env.context.get("archive_reason_provided"):
            return super().action_archive()
        return self._open_archive_reason()

    def action_unarchive(self):
        already_active = self.filtered("active")
        if already_active:
            details = "\n".join("- %s" % r.display_name for r in already_active)
            raise UserError(
                _("Cannot unarchive document(s) that are already active:\n%s") % details
            )
        return super().action_unarchive()
