# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def _get_record_and_check(
        self, xmlid=None, model=None, id=None, field="datas", access_token=None
    ):
        # The HTML editor puts an access token in the link of every file it
        # inserts, and the token alone opens the file to anyone who has the link:
        # Odoo accepts it here, for /web/content and for the routes that check a
        # file the same way. A file of a document page, or of one of its
        # versions, goes only to whoever can read the page, with the token or
        # without it
        if model == "ir.attachment" and id and not xmlid:
            attachment = self.env["ir.attachment"].browse(int(id))
            document_file = attachment.sudo().exists().res_model in (
                "document.page",
                "document.page.history",
            )
            if document_file and not attachment._document_page_file_readable():
                return None, 403
        return super()._get_record_and_check(
            xmlid=xmlid, model=model, id=id, field=field, access_token=access_token
        )
