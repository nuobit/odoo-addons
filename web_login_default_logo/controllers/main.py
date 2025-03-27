# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT 2025 - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import functools
import logging

from odoo import http
from odoo.modules import get_resource_path

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
        placeholder = functools.partial(get_resource_path, "web", "static", "img")
        return http.Stream.from_path(placeholder("nologo.png")).get_response()
