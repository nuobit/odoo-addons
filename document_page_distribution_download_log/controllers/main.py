# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import NotFound
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
    def download_version(self, history_id, attachment_id, **kwargs):
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
        # the version content may still link an attachment deleted afterwards
        attachment = request.env["ir.attachment"].browse(attachment_id).exists()
        if not attachment:
            raise NotFound()
        # mirror /web/content's own access check BEFORE logging: a download
        # row is evidence a covered user reached a valid, readable file link
        # (never log one the redirect would deny with 403, e.g. an attachment
        # not bound to the page); serving the binary and its cache semantics
        # stay in /web/content.
        try:
            attachment.check("read")
        except AccessError:
            raise NotFound() from None
        http_request = request.httprequest
        history._log_recipient_download(
            attachment_id,
            user=request.env.user,
            ip_address=http_request.remote_addr,
            user_agent=http_request.user_agent.string
            if http_request.user_agent
            else False,
        )
        return redirect("/web/content/%s?download=true" % attachment_id, code=303)
