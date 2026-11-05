# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import AccessError


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def _document_page_file_readable(self):
        """Whether the current user may get this file of a document page: they can
        read the page and, when the file holds one of its fields, that field.
        A file of no existing page, such as an upload of a page not saved yet, is
        only for its uploader and the system administrators, as Odoo does with any
        file of no record.
        """
        self.ensure_one()
        file = self.sudo()
        page = self.env["document.page"].browse(file.res_id).exists()
        if not page:
            return self.env.is_system() or file.create_uid == self.env.user
        try:
            page.check_access_rights("read")
            page.check_access_rule("read")
            if file.res_field:
                page.check_field_access_rights("read", [file.res_field])
        except AccessError:
            return False
        return True
