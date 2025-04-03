# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from email_validator import EmailSyntaxError, EmailUndeliverableError, validate_email

from odoo import _

from odoo.addons.auth_signup.controllers.main import AuthSignupHome

_logger = logging.getLogger(__name__)


class AuthSignupValidationEmail(AuthSignupHome):
    def _prepare_passwordless_signup_values(self, values, qcontext):
        values, qcontext = super()._prepare_passwordless_signup_values(values, qcontext)
        # Check good format of e-mail
        try:
            validate_email(values.get("login", ""))
        except EmailSyntaxError as error:
            qcontext["error"] = getattr(
                error,
                "message",
                _("That does not seem to be an email address."),
            )
        except EmailUndeliverableError as error:
            qcontext["error"] = str(error)
        except Exception as error:
            qcontext["error"] = str(error)
        if not values.get("email"):
            values["email"] = values.get("login")
        return values, qcontext

    def _generate_qcontext_message(self, auth_signup_method):
        if auth_signup_method == "email":
            return _("Check your email to activate your account!")
        return super()._generate_qcontext_message(auth_signup_method)
