# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, http
from odoo.http import request

from odoo.addons.auth_signup_verify_email.controllers.main import SignupVerifyEmail
from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)


class SignupVerifyEmailPhone(SignupVerifyEmail):
    def mobile_send_msg_error(self):
        return _(
            "We couldn't send you a message to validate your phone number. "
            "Please try again later, sign in or contact support."
        )

    def get_new_signup_user(self, login, domain=None):
        if domain is None:
            domain = []
        domain = [("login", "=", login), ("state", "=", "new")] + domain
        return request.env["res.users"].sudo().search(domain)

    @http.route()
    def web_login(self, redirect=None, **kw):
        if request.httprequest.method == "POST":
            request.update_context(active_test=False)
            user = self.get_new_signup_user(
                request.params.get("login"), domain=[("active", "=", False)]
            )
            if user:
                partner = user.partner_id
                if (
                    not partner.signup_email_validated
                    or not partner.signup_mobile_validated
                ):
                    if not partner.signup_email_validated:
                        message = _(
                            "Your mobile number has been verified, but your email "
                            "still needs to be validated."
                        )
                    if not partner.signup_mobile_validated:
                        message = _(
                            "Your email has been verified, but your phone number still "
                            "needs to be validated."
                        )
                        if not partner.signup_mobile_token or not request.params.get(
                            "auth_signup"
                        ):
                            try:
                                with request.env.cr.savepoint():
                                    partner.action_resend_whatsapp()
                            except Exception:
                                message = (
                                    _("Your email is verified. ")
                                    + self.mobile_send_msg_error()
                                )
                    return request.render(
                        "auth_signup_verify_email_phone.multi_auth_signup",
                        {"message": message},
                    )
        return super().web_login(redirect, **kw)

    def passwordless_signup(self):
        request.update_context(
            multi_auth_signup=True,
            web_lang=request.params.get("language"),
            active_test=False,
        )
        values = request.params
        qcontext = self.get_auth_signup_qcontext()

        user = self.get_new_signup_user(qcontext.get("login"))
        if user:
            error = []
            if not user.signup_mobile_validated:
                if not user.signup_mobile_token:
                    try:
                        user.partner_id.action_resend_whatsapp()
                        qcontext["message"] = _(
                            "Check your phone to activate your account!"
                        )
                        return request.render("auth_signup.reset_password", qcontext)
                    except Exception as e:
                        _logger.error("Error sending WhatsApp message: %s", str(e))
                        qcontext["error"] = self.mobile_send_msg_error()
                        return request.render("auth_signup.signup", qcontext)
                error.append(_("mobile"))
            if not user.signup_email_validated:
                error.append(_("email"))
            if error:
                qcontext["error"] = _(
                    "Pending verification of your %s."
                ) % " and ".join(error)
                return request.render("auth_signup.signup", qcontext)

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
            return request.render("auth_signup.signup", qcontext)

        res = super().passwordless_signup()

        if res.qcontext.get("error"):
            return res

        user = self.get_new_signup_user(qcontext.get("login"))
        user.active = False
        if not user.signup_mobile_token:
            qcontext["error"] = (
                _("Verification email has been sent. ") + self.mobile_send_msg_error()
            )
            return request.render("auth_signup.signup", qcontext)

        res.qcontext["message"] = _(
            "Check your mobile and email to activate your account!"
        )
        return res

    def do_signup_without_login(self, qcontext):
        values = self._prepare_signup_values(qcontext)
        request.env["res.users"].with_context(active_test=False).sudo().signup(
            values, qcontext.get("token")
        )

    def _handle_user_activation(self, user, qcontext):
        if (
            user.partner_id.signup_email_validated
            and user.partner_id.signup_mobile_validated
        ):
            user.active = True
            qcontext["message"] = _("Your account has been activated!")
            return request.render(
                "auth_signup_verify_email_phone.multi_auth_signup", qcontext
            )
        return False

    @http.route()
    def web_auth_reset_password(self, *args, **kw):
        auth_signup = kw.get("auth_signup", False)
        if auth_signup:
            qcontext = self.get_auth_signup_qcontext()
            user = (
                request.env["res.users"]
                .with_context(active_test=False)
                .sudo()
                .search(
                    [
                        ("email", "=", qcontext.get("signup_email")),
                        ("state", "=", "new"),
                    ],
                    limit=1,
                )
            )
            if user:
                partner = user.partner_id
                if "error" not in qcontext and request.httprequest.method == "POST":
                    self.do_signup_without_login(qcontext)
                    if not user.active:
                        response = self._handle_user_activation(user, qcontext)
                        if response:
                            return response
                    return self.web_login(*args, **kw)
                elif "signup_email" in qcontext:
                    if auth_signup == partner.signup_email_token:
                        partner.signup_email_token = False
                        partner.signup_email_validated = True
                    elif auth_signup == partner.signup_mobile_token:
                        partner.signup_mobile_token = False
                        partner.signup_mobile_validated = True
                    if not user.signup_token:
                        response = self._handle_user_activation(user, qcontext)
                        if response:
                            return response
        return super().web_auth_reset_password(*args, **kw)
