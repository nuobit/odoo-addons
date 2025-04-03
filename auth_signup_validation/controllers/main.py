# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

import werkzeug

from odoo import _, http
from odoo.http import request, route

from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.home import ensure_db

_logger = logging.getLogger(__name__)


class AuthSignupValidation(AuthSignupHome):
    def get_new_signup_user(self, login, domain=None):
        if domain is None:
            domain = []
        domain = [("login", "=", login), ("state", "=", "new")] + domain
        return request.env["res.users"].sudo().search(domain)

    def _prepare_passwordless_signup_values(self, values, qcontext):
        # remove values that could raise "Invalid field '*' on model 'res.users'"
        values.pop("redirect", "")
        values.pop("token", "")
        # Remove password
        values["password"] = ""
        return values, qcontext

    def _create_user_sudo(self, values, qcontext):
        sudo_users = request.env["res.users"].with_context(create_user=True).sudo()
        try:
            with request.cr.savepoint():
                sudo_users.signup(values, qcontext.get("token"))
                sudo_users.reset_password(values.get("login"))
                sudo_users = self.get_new_signup_user(qcontext.get("login"))
        except Exception as error:
            # Duplicate key or wrong SMTP settings, probably
            _logger.exception(error)
            if (
                request.env["res.users"]
                .sudo()
                .search([("login", "=", qcontext.get("login"))])
            ):
                qcontext["error"] = _(
                    "Another user is already registered using this email address."
                )
            else:
                # Agnostic message for security
                qcontext["error"] = _(
                    "Something went wrong, please try again later or contact us."
                )
        return sudo_users, qcontext

    def _generate_qcontext_message(self, auth_signup_method):
        """
        Generate a message for the qcontext based on the auth_signup_method.
        :param auth_signup_method: The authentication signup method.
        :return: A translated message string.
        """
        if auth_signup_method == "all":
            methods = [
                key
                for key, _v in request.env["res.company"]
                .sudo()
                ._fields["auth_signup_method"]
                .selection
                if key not in ["none", "all"]
            ]
            methods = " & ".join(methods)
            return _("Check your %s to activate your account!") % methods
        return ""

    def _check_signup_pending_validation(self):
        """
        Check if passwordless signup is enabled and raise an error if not.
        """
        return False

    @route()
    def web_auth_signup(self, *args, **kw):
        auth_signup_method = request.env.company.auth_signup_method
        if request.params.get("login") and not request.params.get("password"):
            if request.env.company.auth_signup_method != "none":
                return self.passwordless_signup(auth_signup_method)
        res = super().web_auth_signup(*args, **kw)
        res.qcontext["auth_signup_method"] = auth_signup_method
        return res

    def passwordless_signup(self, auth_signup_method):
        request.update_context(
            web_lang=request.params.get("language"),
            auth_signup_method=request.env.company.auth_signup_method,
        )
        values = request.params
        qcontext = self.get_auth_signup_qcontext()
        user = self.get_new_signup_user(
            qcontext.get("login"), domain=[("active", "=", False)]
        )
        msg_error = self._handle_pending_auth_validations(user)
        if msg_error:
            qcontext["error"] = msg_error
            return request.render("auth_signup.signup", qcontext)
        values, qcontext = self._prepare_passwordless_signup_values(values, qcontext)
        if qcontext.get("error"):
            return request.render("auth_signup.signup", qcontext)
        sudo_users, qcontext = self._create_user_sudo(values, qcontext)
        if qcontext.get("error"):
            return request.render("auth_signup.signup", qcontext)
        qcontext["message"] = self._generate_qcontext_message(auth_signup_method)
        if len(sudo_users.partner_id.auth_method_validated) > 1:
            sudo_users.active = False
        return request.render("auth_signup.reset_password", qcontext)

    def _trigger_pending_auth_validation(self, user, method):
        """
        Trigger the pending authentication validation for each method.
        """
        return False

    def _get_auth_validation_error_msg(self, method):
        """
        Return an error message if the given auth method has not been validated.
        """
        return ""

    def _get_pending_methods_message(self, validated, pending):
        """
        Get the message for the pending authentication methods.
        """
        message = []
        if validated:
            message.append(
                _(
                    "You have successfully validated the following authentication methods: %s."
                )
                % ", ".join(validated)
            )
        message.append(
            _("The following authentication methods are still pending validation: %s.")
            % ", ".join(pending)
        )
        return " ".join(message)

    def _handle_pending_auth_validations(self, user):
        """
        Handle pending authentication validations for the user.
        :param user: The res.users record.
        :return: A message string if there are pending validations, otherwise False.
        """
        method_validated = user.partner_id.auth_method_validated
        error = False
        if method_validated:
            pending_validation = {k for k, v in method_validated.items() if not v}
            if pending_validation:
                for method in pending_validation:
                    error = self._trigger_pending_auth_validation(user, method)
                    if error:
                        break
                else:
                    validated = method_validated.keys() - pending_validation
                    error = self._get_pending_methods_message(
                        validated, pending_validation
                    )
        return error

    # TODO: Review es pot evitar que el login sempre tingui el active_test=False?
    @http.route()
    def web_login(self, redirect=None, **kw):
        ensure_db()
        response = super().web_login(redirect, **kw)
        if request.httprequest.method == "POST":
            request.update_context(active_test=False)
            user = self.get_new_signup_user(
                request.params.get("login"), domain=[("active", "=", False)]
            )
            if user:
                # Check if the user has pending authentication validations
                error = self._handle_pending_auth_validations(user)
                if error:
                    response.qcontext["error"] = error
        return response

    def do_signup_without_login(self, qcontext):
        values = self._prepare_signup_values(qcontext)
        request.env["res.users"].with_context(active_test=False).sudo().signup(
            values, qcontext.get("token")
        )

    # TODO: Review els partners no quedan arxivats amb user.active = False
    @http.route()
    def web_auth_reset_password(self, *args, **kw):
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
            m_validated = user.partner_id.auth_method_validated
            if m_validated:
                if "error" not in qcontext and request.httprequest.method == "POST":
                    if len(m_validated) > 1:
                        self.do_signup_without_login(qcontext)
                        # exec _handle_pending_auth_validations
                        error = self._handle_pending_auth_validations(user)
                        if error:
                            return request.render(
                                "auth_signup_validation.multi_auth_signup",
                                {"message": error},
                            )
                        return self.web_login(*args, **kw)
                elif "signup_email" in qcontext:
                    auth_method_token = user.partner_id.auth_method_token
                    if auth_method_token:
                        auth_signup = kw.get("auth_signup", False)
                        if not auth_signup:
                            raise werkzeug.exceptions.NotFound()
                        # Check if the token is valid
                        found = False
                        for method, token in auth_method_token.items():
                            if token == auth_signup:
                                auth_method_token.pop(method)
                                m_validated[method] = True
                                user.partner_id.write(
                                    {
                                        "auth_method_token": auth_method_token,
                                        "auth_method_validated": m_validated,
                                    }
                                )
                                found = True
                                break
                        if not found:
                            qcontext["error"] = _(
                                "This authentication method has already been validated,"
                                " does not exist or has already been used. You have "
                                "pending to validate: %s"
                            ) % " & ".join(auth_method_token.keys())
                            return request.render(
                                "auth_signup.reset_password", qcontext
                            )
                    else:
                        pending_validation = {
                            k: v for k, v in m_validated.items() if not v
                        }
                        if len(m_validated) == 1:
                            for key in pending_validation:
                                m_validated[key] = True
                            user.partner_id.auth_method_validated = m_validated
                    if not auth_method_token and all(m_validated.values()):
                        user.active = True
                        if len(m_validated) > 1:
                            qcontext["message"] = _("Your account has been activated!")
                            return request.render(
                                "auth_signup.reset_password", qcontext
                            )
        return super().web_auth_reset_password(*args, **kw)
