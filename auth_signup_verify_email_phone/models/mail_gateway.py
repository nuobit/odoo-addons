# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class MailGateway(models.Model):
    _inherit = "mail.gateway"

    def _get_gateway_data(self):
        data = super()._get_gateway_data()
        data["default_signup_auth_method"] = self.default_signup_auth_method
        template = self.env["mail.whatsapp.template"].search(
            [("signup_auth", "=", True)]
        )
        data["default_template_by_lang"] = {temp.language: temp.id for temp in template}
        return data

    @api.model
    @tools.ormcache()
    def _get_default_registration_gateway_map(self, state="integrated"):
        result = {}
        for record in self.sudo().search(
            [
                ("integrated_webhook_state", "=", state),
            ]
        ):
            result[record.webhook_key] = record._get_gateway_data()
        return result

    @api.model
    def _get_default_registration_gateway(self):
        # We are using cache in order to avoid an exploit
        gateway_map = self._get_default_registration_gateway_map()
        for _key, gateway_data in gateway_map.items():
            if gateway_data.get("default_signup_auth_method"):
                return gateway_data
        raise ValidationError(
            _("No default registration gateway found. Please configure one.")
        )

    default_signup_auth_method = fields.Boolean(
        string="Default Registration Authentication Method",
        default=False,
        help="Indicates if this is the default method for user registration authentication.",
    )

    @api.constrains("default_signup_auth_method")
    def _check_default_signup_auth_method(self):
        for rec in self:
            if rec.search_count([("default_signup_auth_method", "=", True)]) > 1:
                raise ValidationError(
                    _(
                        "Only one authentication method can be "
                        "the default for user registration."
                    )
                )

    def action_default_signup_auth_method(self):
        self.ensure_one()
        self.default_signup_auth_method = not self.default_signup_auth_method

    def write(self, vals):
        res = super(MailGateway, self).write(vals)
        if "default_signup_auth_method" in vals or "whatsapp_template_ids" in vals:
            self.clear_caches()
        return res
