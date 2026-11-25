# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class DocumentPageHistory(models.Model):
    _inherit = "document.page.history"

    @api.depends("page_id.history_head", "state", "is_approval_required")
    def _compute_editables_locked(self):
        return super()._compute_editables_locked()

    def _editables_lock_message(self):
        """Under approval the editable files of a version follow its content: a
        draft change request changes them, and where the document requires
        approval nothing else does."""
        self.ensure_one()
        if self.state == "draft":
            message = None
        else:
            message = (
                _(
                    'The editable files of "%s" cannot change: under approval, '
                    "only those of a draft change request can.",
                    self.display_name,
                )
                if self.is_approval_required
                else super()._editables_lock_message()
            )
        return message
