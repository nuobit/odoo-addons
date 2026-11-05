# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def binary_content(
        self,
        xmlid=None,
        model="ir.attachment",
        id=None,
        field="datas",
        unique=False,
        filename=None,
        filename_field="name",
        download=False,
        mimetype=None,
        default_mimetype="application/octet-stream",
        access_token=None,
    ):
        # The HTML editor puts an access token in the link of every file it
        # inserts, and the token alone opens the file to anyone who has the link.
        # A file of a document page goes only to whoever can read the page, with
        # the token or without it
        if model == "ir.attachment" and id and not xmlid:
            attachment = self.env["ir.attachment"].browse(int(id))
            if (
                attachment.sudo().exists().res_model == "document.page"
                and not attachment._document_page_file_readable()
            ):
                return 403, [], None
        return super().binary_content(
            xmlid=xmlid,
            model=model,
            id=id,
            field=field,
            unique=unique,
            filename=filename,
            filename_field=filename_field,
            download=download,
            mimetype=mimetype,
            default_mimetype=default_mimetype,
            access_token=access_token,
        )
