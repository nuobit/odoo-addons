# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from contextlib import ExitStack

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class DocumentPageEditableFile(models.Model):
    _name = "document.page.editable.file"
    _description = "Editable file of a document version"
    _order = "sequence, id"

    history_id = fields.Many2one(
        comodel_name="document.page.history",
        string="Version",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string="File name", required=True)
    file = fields.Binary(attachment=True, required=True)

    # A field kept as an attachment has no column, so the database does not hold it
    # required. The version is in the values of every file created, so the check
    # runs for each new file too. It reads the file as its user, and Odoo checks
    # such a read, of a field with no column, on the file as it is in memory: so,
    # where a write checks the rules on the files as they were, it refuses a move
    # into a version that user cannot reach, such as one of another company, with
    # approval installed or not. It must not become a read as superuser. One call
    # escapes it: a write that also sets the file, sent with bin_size in its
    # context, puts the file in Odoo's cache, where this read finds it without a
    # check (the readme's ROADMAP)
    @api.constrains("history_id", "file")
    def _check_file(self):
        for editable_file in self.with_context(bin_size=True):
            if not editable_file.file:
                raise ValidationError(
                    _(
                        'The editable file "%s" has no file: every editable file '
                        "needs one.",
                        editable_file.name,
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        # A user's files are created and checked inside a savepoint, which Odoo
        # rolls back with its cache when the check refuses them: a refused file is
        # gone at once, not only once the request rolls back. The superuser's
        # copies, which the check lets through, need none
        with ExitStack() as refusal:
            if not self.env.su:
                refusal.enter_context(self.env.cr.savepoint())
            # Each file is kept as it was uploaded: Odoo resizes a large image
            # unless told not to
            editable_files = (
                super(
                    DocumentPageEditableFile,
                    self.with_context(image_no_postprocess=True),
                )
                .create(vals_list)
                .with_env(self.env)
            )
            # Checked on the files created, so that a version given by a default
            # counts
            editable_files._check_editables_can_change(editable_files.history_id)
        editable_files.history_id.page_id._touch_rows()
        return editable_files

    def write(self, vals):
        # The versions the files leave, and the one they move to
        versions = self.history_id
        if self and vals.get("history_id"):
            versions |= self.env["document.page.history"].browse(vals["history_id"])
        self._check_editables_can_change(versions)
        result = super(
            DocumentPageEditableFile, self.with_context(image_no_postprocess=True)
        ).write(vals)
        versions.page_id._touch_rows()
        return result

    def unlink(self):
        self._check_editables_can_change(self.history_id)
        documents = self.history_id.page_id
        result = super().unlink()
        documents._touch_rows()
        return result

    def _check_editables_can_change(self, versions):
        """Refuse the change when the editable files of one of ``versions`` can no
        longer change. The superuser changes them anyway: the copy into a new
        version runs as superuser."""
        if not self.env.su:
            messages = [
                message
                for message in (
                    version._editables_lock_message() for version in versions
                )
                if message is not None
            ]
            if messages:
                raise UserError(messages[0])

    def _unlink_attachments(self):
        """Delete the attachments that held the contents of these files once the
        database has deleted the files with their version. Its callers find the
        files as superuser, the one user who may change those attachments."""
        self.env["ir.attachment"].search(
            [
                ("res_model", "=", self._name),
                ("res_field", "=", "file"),
                ("res_id", "in", self.ids),
            ]
        ).unlink()
