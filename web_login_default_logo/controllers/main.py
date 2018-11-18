# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import functools
import logging

from odoo import http
from odoo.modules import get_resource_path

_logger = logging.getLogger(__name__)


class Binary(http.Controller):

    @http.route([
        '/nologo.png',
    ], type='http', auth="none", cors="*")
    def no_logo(self, dbname=None, **kw):
        placeholder = functools.partial(get_resource_path, 'web', 'static', 'src', 'img')

        return http.send_file(placeholder('nologo.png'))
