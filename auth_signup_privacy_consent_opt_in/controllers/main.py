# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import http
from odoo.http import request

from odoo.addons.auth_signup_privacy_consent.controllers.main import (
    AuthSignupHomePrivacyConsent,
)

_logger = logging.getLogger(__name__)


class AuthSignupHomePrivacyConsentOptIn(AuthSignupHomePrivacyConsent):
    def get_privacy_activity_opt_in(self):
        return (
            request.env["privacy.activity"]
            .sudo()
            .search([("is_opt_in", "=", True), ("consent_required", "!=", False)])
        )

    @http.route()
    def web_auth_signup(self, *args, **kw):
        response = super().web_auth_signup(*args, **kw)
        qcontext = self.get_auth_signup_qcontext()
        if "error" not in response.qcontext and request.httprequest.method == "POST":
            opt_in = kw.get("opt_in")
            if opt_in:
                activity = self.get_privacy_activity_opt_in()
                if activity:
                    login = qcontext.get("login")
                    answer = opt_in == "accepted"
                    self._process_privacy_consent(activity, login, answer=answer)
        return response
