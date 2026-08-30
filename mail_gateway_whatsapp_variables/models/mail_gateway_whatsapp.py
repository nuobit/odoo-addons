# Copyright 2025 NuoBiT - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MailGatewayWhatsappService(models.AbstractModel):
    _inherit = "mail.gateway.whatsapp"

    def _send_payload(
        self, channel, body=False, media_id=False, media_type=False, media_name=False
    ):
        payload = super()._send_payload(channel, body, media_id, media_type, media_name)

        if (
            body
            and self.env.context.get("whatsapp_template_id")
            and payload.get("type") == "template"
        ):
            whatsapp_template = self.env["mail.whatsapp.template"].browse(
                self.env.context.get("whatsapp_template_id")
            )
            variables = whatsapp_template.get_variable_values()
            body_variables = variables.get("body")

            if body_variables and variables["type"] == "number":
                parameters = [
                    {"type": "text", "text": value} for value in body_variables.values()
                ]
                payload["template"]["components"] = [
                    {"type": "body", "parameters": parameters}
                ]

        return payload
