# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError

# The fields that attach a file to its record or hold what its link serves.
# The file size, the checksum and the stored file name are not listed: the
# write of ir.attachment drops them.
KEPT_FILE_FIELDS = (
    "res_model",
    "res_id",
    "res_field",
    "datas",
    "raw",
    "db_datas",
    "type",
)


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    document_page_content_file = fields.Boolean(
        readonly=True,
        copy=False,
        groups="base.group_system",
        help="Linked in the content of a saved version of its document page. "
        "While the page exists, only a system administrator can delete it, "
        "attach it to another record or change its content.",
    )

    def _check_document_page_content_files(self):
        """Refuse to a user who is not a system administrator any change of the
        files kept with an existing document page: the files saved in the
        content of its versions.
        """
        if not self.env.is_system():
            content_files = self.filtered(
                lambda a: a.res_model == "document.page"
                and a.sudo().document_page_content_file
            )
            pages = (
                self.env["document.page"]
                .browse(sorted(set(content_files.mapped("res_id"))))
                .exists()
            )
            if pages:
                lines = [
                    "- %s: %s"
                    % (
                        page.display_name,
                        ", ".join(
                            content_files.filtered_domain(
                                [("res_id", "=", page.id)]
                            ).mapped("name")
                        ),
                    )
                    for page in pages
                ]
                raise UserError(
                    _(
                        "These files are kept with the versions of their document: "
                        "while the document exists, only a system administrator can "
                        "delete them, attach them to another record or change their "
                        "content.\n%s",
                        "\n".join(lines),
                    )
                )

    def write(self, vals):
        if any(field in vals for field in KEPT_FILE_FIELDS):
            self._check_document_page_content_files()
        return super().write(vals)

    def unlink(self):
        self._check_document_page_content_files()
        return super().unlink()
