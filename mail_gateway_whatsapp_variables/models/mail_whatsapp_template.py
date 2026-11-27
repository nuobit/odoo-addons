# Copyright 2025 NuoBiT - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailWhatsAppTemplate(models.Model):
    _inherit = "mail.whatsapp.template"

    variable_ids = fields.One2many(
        comodel_name="mail.whatsapp.template.variable", inverse_name="template_id"
    )
    variable_type = fields.Selection(selection=[("number", "Number"), ("name", "Name")])

    def get_variable_values(self):
        values = {"type": self.variable_type}
        body_variables = self.variable_ids.filtered(lambda x: x.section == "body")
        if body_variables:
            body = {}
            for variable in body_variables:
                body.update({variable.name: variable.default_value})
            values.update({"body": body})
        return values

    def get_body(self):
        values = self.get_variable_values()
        body_variables = values.get("body")
        body = self.body
        if body_variables:
            for key, value in body_variables.items():
                body = body.replace(f"{{{{{key}}}}}", value)
        return body

    def button_sync_template(self):
        self.variable_ids.unlink()
        return super().button_sync_template()

    @classmethod
    def _prepare_values_to_import(cls, gateway, json_data):
        vals = super()._prepare_values_to_import(gateway, json_data)

        for component in json_data.get("components", []):
            if component["type"] == "BODY":
                for key, value in component.get("example", {}).items():
                    if key == "body_text":
                        vals["variable_type"] = "number"
                        for var_list in value:
                            for variable, var_value in enumerate(var_list, start=1):
                                vals.setdefault("variable_ids", []).append(
                                    (
                                        0,
                                        0,
                                        {
                                            "section": "body",
                                            "name": variable,
                                            "parameter_type": "text",
                                            "default_value": var_value,
                                        },
                                    )
                                )
        return vals
