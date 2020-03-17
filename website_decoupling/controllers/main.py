# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import http

from odoo.addons.website.controllers.main import Website

import re

_logger = logging.getLogger(__name__)


class WebsiteDecoupled(Website):

    def _is_erp_host(self):
        IrConfig = http.request.env['ir.config_parameter'].sudo()
        erp_hosts_regexp = IrConfig.get_param('website.erp.hosts')
        if erp_hosts_regexp:
            current_host = http.request.httprequest.host.split(':')[0]
            return bool(re.match(r'%s' % erp_hosts_regexp, current_host))
        return False

    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        if self._is_erp_host() and not http.request.env.user.has_group(
                'website_decoupling.group_website_decoupling_bypass'):
            return http.local_redirect('/web', query=http.request.params, keep_hash=True)
        else:
            return super(WebsiteDecoupled, self).index(**kw)

    @http.route(website=True, auth="public")
    def web_login(self, redirect=None, *args, **kw):
        response = super(WebsiteDecoupled, self).web_login(redirect=redirect, *args, **kw)
        response.qcontext['hide_website_layout'] = self._is_erp_host()
        return response
