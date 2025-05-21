# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class BarcodeLabelTemplateWizard(models.TransientModel):
    _name = "barcode.label.template.wizard"
    _description = "Barcode Label Template Wizard"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        default_configuration = self.env["barcode.label.template.configuration"].search(
            [("default", "=", True)],
        )
        if default_configuration:
            res["barcode_label_template_configuration_id"] = default_configuration.id
        return res

    barcode_label_template_configuration_id = fields.Many2one(
        comodel_name="barcode.label.template.configuration",
        required=True,
    )

    def print_barcodes_with_template(self):
        return (
            self.env.ref("barcode_label_template.action_report_barcode_label_template")
            .with_context(
                paperformat_id=self.barcode_label_template_configuration_id.paperformat_id.id,
                template_configuration_id=self.barcode_label_template_configuration_id.id,
            )
            .report_action(
                self,
                data={
                    "active_ids": self.env.context.get("active_ids"),
                },
            )
        )
