# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MailWhatsAppTemplate(models.Model):
    _inherit = "mail.whatsapp.template"

    signup_auth = fields.Boolean(
        string="Use as authenticator for signup",
    )

    def get_variable_values(self):
        values = super().get_variable_values()
        variables_values = self.env.context.get("variables_values", {})
        if variables_values:
            for key, value in variables_values.items():
                values.update({key: value})
        return values

    def action_signup_auth(self):
        self.ensure_one()
        self.signup_auth = not self.signup_auth

    @api.constrains("is_supported", "signup_auth")
    def _check_signup_auth(self):
        for rec in self:
            if rec.signup_auth and not rec.is_supported:
                raise ValidationError(
                    _(
                        "Only supported templates can be the "
                        "default for authentication signup."
                    )
                )
            if (
                rec.search_count(
                    [
                        ("signup_auth", "=", True),
                        ("language", "=", rec.language),
                        ("gateway_id", "=", rec.gateway_id.id),
                    ]
                )
                > 1
            ):
                raise ValidationError(
                    _(
                        "Only one template can be the default for authentication "
                        "signup for the same language."
                    )
                )

    def get_custom_template_payload_body_values(self):
        parameters = []
        for body in self.body_ids:
            parameters.append(
                {
                    "type": body.parameter_type,
                    "text": body.default_value,
                }
            )
        return parameters
