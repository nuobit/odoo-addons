# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo.http import request

from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home

_logger = logging.getLogger(__name__)


class OAuthLogin(Home):
    def get_auth_signup_qcontext(self):
        result = super().get_auth_signup_qcontext()
        result.update(
            {k: v for k, v in request.params.items() if k in ["language", "mobile"]}
        )
        return result

    def _prepare_signup_values(self, qcontext):
        values = super()._prepare_signup_values(qcontext)
        values.update({k: v for k, v in qcontext.items() if k in ["mobile"]})
        language = qcontext.get("language")
        if language:
            values["lang"] = language
        return values
