# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from werkzeug.exceptions import NotFound
from werkzeug.urls import url_encode
from werkzeug.utils import redirect

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request

_logger = logging.getLogger(__name__)

# the Sec-Fetch-Dest values of a request whose response the browser hands to
# the user: the navigation requests of the Fetch standard (a click, a new tab,
# a link clicked inside a frame) and "empty", the value of a request with no
# destination of its own (a save or a download, and a script's request)
SERVED_DESTINATIONS = ("document", "embed", "frame", "iframe", "object", "empty")
# the other destinations of the Fetch standard: a part of another page (an
# image, a media file, a font, a style sheet, a script), a worker, a report;
# they are refused without a word
OTHER_FETCH_DESTINATIONS = (
    "audio",
    "audioworklet",
    "font",
    "image",
    "json",
    "manifest",
    "paintworklet",
    "report",
    "script",
    "serviceworker",
    "sharedworker",
    "style",
    "text",
    "track",
    "video",
    "webidentity",
    "worker",
    "xslt",
)
# the headers by which a browser says it asks ahead of the user: Sec-Purpose,
# and the ones older browsers sent instead (Purpose by Chrome, X-Purpose by
# WebKit and Safari, X-Moz by Firefox)
PREFETCH_HEADERS = ("Sec-Purpose", "Purpose", "X-Purpose", "X-Moz")


class DocumentPageDistributionDownloadLogController(http.Controller):
    @http.route(
        "/document_page_distribution_download_log/download"
        "/<int:history_id>/<int:attachment_id>",
        type="http",
        auth="user",
        methods=["GET"],
    )
    def download_version(self, history_id, attachment_id, access_token=None, **kwargs):
        # an address the browser declares as asked for a part of another page
        # (an image, a script) or ahead of the user (a prefetch) hands no file
        # to the user: no row, and the 404 of an address that does not exist
        if not self._response_goes_to_user():
            raise NotFound()
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
        # the check of /web/content itself: a row is written only when
        # /web/content would let the user read the file
        attachment, _status = request.env["ir.http"]._get_record_and_check(
            model="ir.attachment", id=attachment_id, access_token=access_token
        )
        if not attachment:
            raise NotFound()
        # a HEAD asks for the headers only: it gets the answer of the GET and,
        # since no file leaves, no row
        if request.httprequest.method == "GET":
            history._log_recipient_download(attachment_id)
        query = {"download": "true"}
        if access_token:
            query["access_token"] = access_token
        url = "/web/content/%s?%s" % (attachment_id, url_encode(query))
        return redirect(url, code=303)

    def _response_goes_to_user(self):
        """Whether the browser asks for the address to hand the response to the
        user. A request without Sec-Fetch-Dest (an older browser, a site over
        plain HTTP other than localhost, a program) is taken as one."""
        headers = request.httprequest.headers
        if any(header in headers for header in PREFETCH_HEADERS):
            return False
        destination = headers.get("Sec-Fetch-Dest")
        if destination is None or destination in SERVED_DESTINATIONS:
            return True
        # a destination the Fetch standard does not name may be a new kind of
        # navigation: its refusal is logged, so that it can be seen
        if destination not in OTHER_FETCH_DESTINATIONS:
            _logger.info("Download address refused: Sec-Fetch-Dest=%s", destination)
        return False
