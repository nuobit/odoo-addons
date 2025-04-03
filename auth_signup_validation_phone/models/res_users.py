# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    def action_reset_password_extended(self):
        res = super().action_reset_password_extended()
        res["mobile"] = self.send_whatsapp_signup_message
        return res

    @api.model
    def _format_mobile_number(self, mobile):
        mobile = mobile.strip().replace(" ", "")
        if mobile.startswith("+"):
            mobile = mobile[1:]
        return mobile

    def _get_channel_values(self, gateway):
        mobile = self._format_mobile_number(self.mobile)
        return {
            "metadata": {"phone_number_id": gateway.whatsapp_from_phone},
            "contacts": [{"profile": {"name": self.name}, "wa_id": mobile}],
            "messages": [{"from": gateway.whatsapp_from_phone, "to": mobile}],
        }

    def _validate_and_get_whatsapp_channel(self):
        lang = self.env.context.get("web_lang", self.env.lang)
        bot_data = (
            self.env["mail.gateway"]
            .with_context(lang=lang)
            ._get_default_registration_gateway()
        )

        dispatcher = self.env["mail.gateway.whatsapp"].with_user(
            bot_data["webhook_user_id"]
        )
        gateway = dispatcher.env["mail.gateway"].browse(bot_data["id"])
        if not gateway:
            raise ValidationError(_("No WhatsApp gateway configured for verification."))
        if not self.mobile:
            raise ValidationError(_("Phone number is required for verification."))

        chat = dispatcher._get_channel(
            gateway,
            self._format_mobile_number(self.mobile),
            self._get_channel_values(gateway),
            force_create=True,
        )

        lang = self.env["res.lang"].search([("code", "=", lang)], limit=1)
        template_id = bot_data["default_template_by_lang"].get(
            lang.iso_code
        ) or bot_data["default_template_by_lang"].get(lang.code)
        if not template_id:
            raise ValidationError(
                _("WhatsApp template not found for the language %s.") % lang.name
            )

        whatsapp_template = self.env["mail.whatsapp.template"].browse(template_id)
        if not whatsapp_template.exists():
            raise ValidationError(_("WhatsApp template doesn't exist or was deleted."))

        return chat, whatsapp_template

    def _get_template_variables(self, whatsapp_template):
        if self.env.context.get("auth_signup_method") in ["mobile", "all"]:
            self = self.with_context(auth_signup_mobile=True)

        variables_values = {"body": {}}
        for variable in whatsapp_template.variable_ids.filtered(
            lambda x: x.section == "body"
        ):
            field_name = variable.signup_field_id.name
            if not field_name:
                raise ValidationError(
                    _("The WhatsApp template lacks a signup field for %s.")
                    % variable.name
                )
            variables_values["body"][variable.name] = self[field_name]
        return variables_values

    def send_whatsapp_signup_message(self):
        self.mapped("partner_id").signup_prepare(signup_type="reset")
        chat, whatsapp_template = self._validate_and_get_whatsapp_channel()
        variables_values = self._get_template_variables(whatsapp_template)
        body = whatsapp_template.with_context(
            variables_values=variables_values
        ).get_body()
        return chat.with_context(
            whatsapp_template_id=whatsapp_template.id, variables_values=variables_values
        ).message_post(
            body=body,
            author_id=False,
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            date=fields.Datetime.now(),
            raise_exception=True,
        )
