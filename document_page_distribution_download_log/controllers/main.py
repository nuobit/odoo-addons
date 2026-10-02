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
        # a version that does not exist and a version the user cannot read
        # both answer 404, so the route does not say whether a version exists
        history = request.env["document.page.history"].browse(history_id).exists()
        if not history:
            raise NotFound()
        try:
            page = history.page_id
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
