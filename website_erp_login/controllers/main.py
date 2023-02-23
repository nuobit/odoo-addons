# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import http
from odoo.http import request

from odoo.addons.website.controllers.main import Website


class WebsiteERPLogin(Website):
    @http.route("/", type="http", auth="none")
    def index(self, s_action=None, db=None, **kw):
        return http.local_redirect("/web", query=request.params, keep_hash=True)
