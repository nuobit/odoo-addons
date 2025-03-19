# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT 2025 - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import http
from odoo.http import request

from odoo.addons.website.controllers.main import Website


class WebsiteERPLogin(Website):
    @http.route("/", type="http", auth="none")
    def index(self, s_action=None, db=None, **kw):
        return request.redirect_query("/web", query=request.params)
