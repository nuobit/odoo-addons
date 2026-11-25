# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class DocumentPageHistory(models.Model):
    _name = "document.page.history"
    _inherit = ["document.page.history", "document.page.editable.mixin"]

    editable_file_ids = fields.One2many(
        comodel_name="document.page.editable.file",
        inverse_name="history_id",
        string="Editables",
        groups="document_page.group_document_editor",
        copy=False,
    )
    editables_locked = fields.Boolean(
        compute="_compute_editables_locked",
        help="The editable files of this version can no longer change.",
    )

    @api.depends("page_id.history_head")
    def _compute_editables_locked(self):
        # Decided on the saved version; one not saved yet keeps no files, and its
        # form keeps the list read-only until it is saved
        for version in self:
            version.editables_locked = (
                version._origin._editables_lock_message() is not None
                if version._origin
                else False
            )

    @api.model_create_multi
    def create(self, vals_list):
        # A new version starts with the editable files of its origin, as it starts
        # with its content, unless it is given files of its own: the version it is
        # duplicated from when copy makes it in that version's document, otherwise
        # the version its document showed before it. Read and copied as superuser:
        # whoever changes the content keeps them, also a user who cannot see them.
        # Only copy names the origin, passing the version itself: no API call
        # carries a record, so no API caller names a version other than the one it
        # duplicates; and only in the origin's own document, so that no copy takes
        # files out of their document. The document comes from the values or, as on
        # the screens, from the context's default
        no_version = self.env["document.page.history"]
        value = self.env.context.get("editable_files_origin")
        origin = (
            value.sudo()
            if isinstance(value, models.BaseModel) and value._name == self._name
            else no_version
        )
        default_page_id = self.env.context.get("default_page_id")
        page_ids = [
            vals["page_id"] if "page_id" in vals else default_page_id
            for vals in vals_list
        ]
        shown = {
            page.id: page.history_head
            for page in self.env["document.page"]
            .sudo()
            .browse([page_id for page_id in page_ids if page_id])
        }
        versions = super().create(vals_list)
        for version in versions.sudo():
            if not version.editable_file_ids:
                version._copy_editable_files_from(
                    origin
                    if origin.page_id == version.page_id
                    else shown.get(version.page_id.id, no_version)
                )
        return versions

    def copy(self, default=None):
        # The duplicate is a version made from this one, so create gives it the
        # editable files of this version unless its default gives it files of its
        # own or another document. Create gets this version as a record, which no
        # API call can carry. The duplicate comes back in the caller's
        # environment, without that record, so that a later version made through
        # it starts from the one its document shows
        self.ensure_one()
        duplicate = super(
            DocumentPageHistory, self.with_context(editable_files_origin=self)
        ).copy(default=default)
        return duplicate.with_env(self.env)

    def unlink(self):
        # The database deletes the editable files of these versions with them, but
        # not the attachments that hold their contents: those go once the versions
        # are deleted, after every check Odoo makes of the deletion
        editable_files = (
            self.env["document.page.editable.file"]
            .sudo()
            .search([("history_id", "in", self.ids)])
        )
        result = super().unlink()
        editable_files._unlink_attachments()
        return result

    def _editables_lock_message(self):
        """Why the editable files of this version cannot change, or None when they
        can: only the version its document shows changes, so that the files of
        the earlier ones stay as they were. The document is read as superuser, so
        that the lock decides alike for every user who may change the files."""
        self.ensure_one()
        return (
            _(
                'The editable files of "%s" cannot change: only those of the '
                "version its document shows can.",
                self.display_name,
            )
            if self.sudo().page_id.history_head != self
            else None
        )

    def _copy_editable_files_from(self, source):
        """Give this version a copy of the editable files of the version
        ``source``, which may be none."""
        self.ensure_one()
        self.env["document.page.editable.file"].create(
            [
                file_vals
                for editable_file in source.with_context(
                    bin_size=False
                ).editable_file_ids
                for file_vals in editable_file.copy_data(
                    default={"history_id": self.id}
                )
            ]
        )
