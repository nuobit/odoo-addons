# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .document_page_editable_mixin import EDITABLE_FILES


def _on_copies(commands, copy_ids):
    """The ``commands`` of a list of editable files, with each file they name
    replaced by its copy in ``copy_ids``, when it has one."""

    def on_copy(command):
        code = command[0]
        if code in (1, 2, 3, 4):
            return (code, copy_ids.get(command[1], command[1]), *command[2:])
        if code == 6:
            return (6, 0, [copy_ids.get(file_id, file_id) for file_id in command[2]])
        return command

    return [on_copy(command) for command in commands]


class DocumentPage(models.Model):
    _name = "document.page"
    _inherit = ["document.page", "document.page.editable.mixin"]

    # The editable files of the version the document shows, changed here as on that
    # version: create and write below save them. Read as the user: the group of a
    # field that is not stored holds for read(), not for an export, which then reads
    # the version's field and its group
    editable_file_ids = fields.One2many(
        comodel_name="document.page.editable.file",
        related="history_head.editable_file_ids",
        related_sudo=False,
        readonly=False,
        string="Editables",
        groups="document_page.group_document_editor",
    )
    editables_locked = fields.Boolean(
        compute="_compute_editables_locked",
        help="The editable files this document shows can no longer change.",
    )

    @api.depends("history_head.editables_locked")
    def _compute_editables_locked(self):
        for page in self:
            page.editables_locked = page.history_head.editables_locked

    @api.model_create_multi
    def create(self, vals_list):
        # The files given with a new document are those of its first version, which
        # the rest of its values makes
        commands_list = [vals.get(EDITABLE_FILES) for vals in vals_list]
        if all(commands is None for commands in commands_list):
            return super().create(vals_list)
        self.check_field_access_rights("write", [EDITABLE_FILES])
        pages = super().create(
            [
                {name: value for name, value in vals.items() if name != EDITABLE_FILES}
                for vals in vals_list
            ]
        )
        no_version = self.env["document.page.history"]
        for page, commands in zip(pages, commands_list):
            page._write_editable_files(commands, no_version)
        return pages

    def write(self, vals):
        # A save of the document can change its content, which makes a new version,
        # and its files. The rest of the values is saved first, so that the files
        # change on the version the document then shows, and the version it showed
        # before keeps its own as they were
        if EDITABLE_FILES not in vals:
            return super().write(vals)
        self.check_field_access_rights("write", [EDITABLE_FILES])
        commands = vals[EDITABLE_FILES]
        shown_before = {page: page.sudo().history_head for page in self}
        result = super().write(
            {name: value for name, value in vals.items() if name != EDITABLE_FILES}
        )
        for page in self:
            page._write_editable_files(commands, shown_before[page])
        return result

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

    def _write_editable_files(self, commands, shown_before):
        """Apply ``commands``, written on the list of editable files of this
        document, to the files of the version it shows, as its user and under the
        lock of that version. The list was read from ``shown_before``, the version
        the document showed before its save: when the save made a new version,
        which started with a copy of those files made in their order, each file
        the commands name is replaced by its copy. Both orders are read from the
        database, as the copy read its own."""
        self.ensure_one()
        if not commands:
            return
        version = self.history_head
        if not version:
            raise UserError(
                _(
                    '"%s" shows no version yet: its editable files are kept with '
                    "its versions.",
                    self.display_name,
                )
            )
        if version != shown_before:
            copy_ids = dict(
                zip(
                    shown_before.editable_file_ids.sorted().ids,
                    version.sudo().editable_file_ids.sorted().ids,
                )
            )
            commands = _on_copies(commands, copy_ids)
        version.write({EDITABLE_FILES: commands})

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
