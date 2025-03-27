# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import http
from odoo.http import request

from odoo.addons.auth_signup_privacy_consent.controllers.main import (
    AuthSignupHomePrivacyConsent,
)

_logger = logging.getLogger(__name__)


class AuthSignupHomePrivacyConsentPolicy(AuthSignupHomePrivacyConsent):
    def get_privacy_policy(self):
        return (
            request.env["privacy.activity"]
            .sudo()
            .search([("privacy_policy", "=", True), ("consent_required", "!=", False)])
        )

    @http.route(
        "/web/privacy_policy",
        type="http",
        auth="public",
        website=True,
    )
    def privacy_policy_description(self, *args, **kwargs):
        policy = self.get_privacy_policy()
        return request.render(
            "auth_signup_privacy_consent_policy.privacy_policy",
            {"description": policy.description},
        )

    @http.route()
    def web_auth_signup(self, *args, **kw):
        response = super().web_auth_signup(*args, **kw)
        qcontext = self.get_auth_signup_qcontext()
        if "error" not in response.qcontext and request.httprequest.method == "POST":
            policy = self.get_privacy_policy()
            if policy:
                self._process_privacy_consent(policy, qcontext.get("login"))
        return response
