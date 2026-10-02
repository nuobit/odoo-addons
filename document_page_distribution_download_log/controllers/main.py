# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import NotFound
from werkzeug.urls import url_encode
from werkzeug.utils import redirect

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request


class DocumentPageDistributionDownloadLogController(http.Controller):
    @http.route(
        "/document_page_distribution_download_log/download"
        "/<int:history_id>/<int:attachment_id>",
        type="http",
        auth="user",
        methods=["GET"],
    )
    def download_version(self, history_id, attachment_id, access_token=None, **kwargs):
        # resolve-then-authorize: sudo only resolves the version; the access
        # gate is the page read check below, run as the requesting user.
        # Missing and forbidden both answer 404 so the route does not reveal
        # whether a version exists.
        history = (
            request.env["document.page.history"].sudo().browse(history_id).exists()
        )
        if not history:
            raise NotFound()
        page = request.env["document.page"].browse(history.page_id.id)
        try:
            page.check_access_rights("read")
            page.check_access_rule("read")
        except AccessError:
            raise NotFound() from None
        if not history._download_attachment_is_tracked(attachment_id):
            raise NotFound()
        # the check of /web/content itself, so that a row is written exactly
        # when the file is going to be served
        attachment, _status = request.env["ir.http"]._get_record_and_check(
            model="ir.attachment", id=attachment_id, access_token=access_token
        )
        if not attachment:
            raise NotFound()
        history._log_recipient_download(attachment_id)
        query = {"download": "true"}
        if access_token:
            query["access_token"] = access_token
        url = "/web/content/%s?%s" % (attachment_id, url_encode(query))
        return redirect(url, code=303)
