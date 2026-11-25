# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class DocumentPage(models.Model):
    _name = "document.page"
    _inherit = ["document.page", "document.page.editable.mixin"]

    # The editable files of the version the document shows. Read as the user: the
    # group of a field that is not stored holds for read(), not for an export,
    # which then reads the version's field and its group
    editable_file_ids = fields.One2many(
        comodel_name="document.page.editable.file",
        related="history_head.editable_file_ids",
        related_sudo=False,
        string="Editables",
        groups="document_page.group_document_editor",
    )

    def unlink(self):
        # The database deletes the versions of these documents with them, and their
        # editable files, but not the attachments that hold the files' contents:
        # those go once the documents are deleted, after every check Odoo makes of
        # the deletion. Found by their version's document, not through history_ids,
        # which document_page_approval limits to approved versions
        editable_files = (
            self.env["document.page.editable.file"]
            .sudo()
            .search([("history_id.page_id", "in", self.ids)])
        )
        result = super().unlink()
        editable_files._unlink_attachments()
        return result

    def action_open_shown_version(self):
        """Open the version the document shows: its editable files are changed
        there."""
        self.ensure_one()
        if not self.history_head:
            raise UserError(
                _(
                    '"%s" shows no version yet: its editable files are kept with '
                    "its versions.",
                    self.display_name,
                )
            )
        return {
            "type": "ir.actions.act_window",
            "res_model": "document.page.history",
            "res_id": self.history_head.id,
            "view_mode": "form",
        }

    def _touch_rows(self):
        """Update the rows of these documents without changing a value, as a new
        version does when it becomes the one its document shows (the stored
        ``history_head``). Of two transactions that change one document's
        editable files, or make a new version of it, the later one then fails on
        the conflict, since Odoo runs at REPEATABLE READ, and Odoo runs it again:
        it then sees the other's change, instead of a change staying on a version
        that is no longer the one its document shows."""
        self.env.cr.execute(
            "UPDATE document_page SET write_date = write_date WHERE id = ANY(%s)",
            [list(self.ids)],
        )
