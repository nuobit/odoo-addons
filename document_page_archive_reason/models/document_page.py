# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class DocumentPage(models.Model):
    _inherit = "document.page"

    active = fields.Boolean(tracking=True)
    archive_reason = fields.Text(
        string="Archive Reason",
        readonly=True,
        copy=False,
    )

    def _check_can_archive_with_reason(self):
        self.invalidate_cache(["active"], self.ids)
        already_archived = self.filtered(lambda page: not page.active)
        if already_archived:
            details = "\n".join("- %s" % page.display_name for page in already_archived)
            raise UserError(
                _("Cannot archive document(s) that are already archived:\n%s") % details
            )
        return self

    def _open_archive_reason(self):
        records = self._check_can_archive_with_reason()
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
        if self.env.context.get("archive_reason_validated"):
            return super().action_archive()
        return self._open_archive_reason()

    def action_unarchive(self):
        archived = self.filtered(lambda page: not page.active)
        res = super().action_unarchive()
        archived.archive_reason = False
        return res
