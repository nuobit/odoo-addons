# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions SL 2025 - Bijaya Kumal <bkumal@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


import logging

from odoo import http
from odoo.tools.misc import file_path

_logger = logging.getLogger(__name__)


class Binary(http.Controller):
    @http.route(
        [
            "/nologo.png",
        ],
        type="http",
        auth="none",
        cors="*",
    )
    def no_logo(self, dbname=None, **kw):
        return http.Stream.from_path(
            file_path("web/static/img/nologo.png")
        ).get_response()
