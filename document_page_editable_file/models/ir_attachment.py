# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import AccessError

EDITABLE_FILE = "document.page.editable.file"


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.model
    def check(self, mode, values=None):
        # Odoo lets a system administrator past its refusal of a field's file, and
        # then the model's rights decide alone: writing an editable file's
        # attachment directly, or giving it a public link, would get past the new
        # model's own checks. Those attachments change only through the new
        # model, which writes them as superuser
        super().check(mode, values=values)
        if mode != "read" and not self.env.su and self._holds_editable_files(values):
            raise AccessError(
                _(
                    "The attachment of an editable file cannot be changed directly: "
                    "change the file on the Editables tab of its version, while its "
                    "files can change."
                )
            )

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        # Odoo 14 leaves the files of the records a user cannot read out of a search
        # of attachments, but not out of a grouped read, which counts them and
        # answers guesses about their indexed text (Odoo 18 builds a grouped read
        # from the search). The editable files are left out of it for whoever
        # cannot read them: all of them without the right to read the model, and
        # those of the records its rules hide otherwise. The superuser reads them
        # all, as Odoo's own check of attachments lets it
        return super().read_group(
            domain
            if self.env.su
            else self._editable_files_read_domain() + list(domain),
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )

    def _holds_editable_files(self, values):
        """Whether one of these attachments holds an editable file, or the values
        written make one of them, or a new one, hold it. Read by SQL, as Odoo's own
        check reads the attachments: a read as superuser here would fill the cache
        that the user's own reads take afterwards."""
        self.env.cr.execute(
            "SELECT 1 FROM ir_attachment WHERE id = ANY(%s) AND res_model = %s "
            "LIMIT 1",
            [list(self.ids), EDITABLE_FILE],
        )
        return self.env.cr.fetchone() is not None or (
            values is not None and values.get("res_model") == EDITABLE_FILE
        )

    @api.model
    def _editable_files_read_domain(self):
        """The domain that leaves out of a grouped read of attachments the editable
        files the user cannot read: given as their ids, which a group's domain
        carries back to the client."""
        files = self.env[EDITABLE_FILE]
        return (
            [
                "|",
                ("res_model", "!=", EDITABLE_FILE),
                ("res_id", "in", files.search([]).ids),
            ]
            if files.check_access_rights("read", raise_exception=False)
            else [("res_model", "!=", EDITABLE_FILE)]
        )
