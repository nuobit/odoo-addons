# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class Report(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def _run_wkhtmltopdf(
        self,
        bodies,
        header=None,
        footer=None,
        landscape=False,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        temp_config_id = self.env.context.get("template_configuration_id")
        if temp_config_id:
            temp_config = self.env["barcode.label.template.configuration"].browse(
                temp_config_id
            )
            original_watermark = self.pdf_watermark
            self.pdf_watermark = temp_config.template
            original_paperformat_id = self.paperformat_id
            self.paperformat_id = temp_config.paperformat_id
        result = super(Report, self)._run_wkhtmltopdf(
            bodies,
            header=header,
            footer=footer,
            landscape=landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )
        if temp_config_id:
            self.pdf_watermark = original_watermark
            self.paperformat_id = original_paperformat_id
        return result
