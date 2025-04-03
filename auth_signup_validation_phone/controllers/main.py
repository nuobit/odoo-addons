# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _
from odoo.http import request

from odoo.addons.auth_signup_validation.controllers.main import AuthSignupValidation
from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)


class AuthSignupValidationPhone(AuthSignupValidation):
    def _trigger_pending_auth_validation(self, user, method):
        res = super()._trigger_pending_auth_validation(user, method)
        m_validated = user.partner_id.auth_method_validated
        m_token = user.partner_id.auth_method_token
        if (
            "mobile" in m_validated
            and m_validated["mobile"] is False
            and not m_token.get("mobile")
        ):
            context = {
                "create_user": True,
                "auth_signup_mobile": True,
                "signup_force_type_in_url": "reset",
            }
            if len(m_validated) > 1:
                context["auth_signup_method"] = "all"
            try:
                with request.env.cr.savepoint():
                    user.with_context(**context).send_whatsapp_message()
            except Exception:
                return _(
                    "You have pending mobile validation. We couldn't send you a "
                    "message to validate your phone number. Please try again later, "
                    "sign in or contact support."
                )
        return res

    def _prepare_passwordless_signup_values(self, values, qcontext):
        values, qcontext = super()._prepare_passwordless_signup_values(values, qcontext)
        try:
            phone_number = phone_validation.phone_format(
                number=values.get("mobile", ""),
                country_code=False,
                country_phone_code=False,
                force_format="INTERNATIONAL",
                raise_exception=True,
            )
            values["mobile"] = phone_number
        except Exception:
            qcontext["error"] = _(
                "Invalid phone number format. Please use the format:<br/>"
                "+[Country Code][Number]<br/>"
                "Example: +34612345758"
            )
        return values, qcontext

    def _generate_qcontext_message(self, auth_signup_method):
        if auth_signup_method == "mobile":
            return _("Check your mobile to activate your account!")
        return super()._generate_qcontext_message(auth_signup_method)
