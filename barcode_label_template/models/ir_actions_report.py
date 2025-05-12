# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import io

from PyPDF2 import PdfFileMerger, PdfFileReader

from odoo import api, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        if self.env.context.get("template_configuration_id"):
            pdf_merger = PdfFileMerger()
            for active_id in data["active_ids"]:
                new_data = data.copy()
                new_data["active_ids"] = [active_id]
                pdf_content_chunk, _ = super()._render_qweb_pdf(
                    report_ref, res_ids=res_ids, data=new_data
                )

                pdf_mem_file_chunk = io.BytesIO()
                pdf_mem_file_chunk.write(pdf_content_chunk)
                pdf_chunk = PdfFileReader(pdf_mem_file_chunk)
                pdf_merger.append(pdf_chunk, import_outline=False)
                pdf_mem_file_chunk.close()

            if pdf_merger:
                pdf_mem_file = io.BytesIO()
                pdf_merger.write(pdf_mem_file)
                pdf_content = pdf_mem_file.getvalue()
                pdf_mem_file.close()
        else:
            pdf_content, _ = super()._render_qweb_pdf(
                report_ref, res_ids=res_ids, data=data
            )

        return pdf_content, "pdf"

    @api.model
    def _run_wkhtmltopdf(
        self,
        bodies,
        report_ref=False,
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
            self = self.env["ir.actions.report"]._get_report_from_name(report_ref)
            original_watermark = self.pdf_watermark
            self.pdf_watermark = temp_config.template
            original_paperformat_id = self.paperformat_id
            self.paperformat_id = temp_config.paperformat_id
        result = super(IrActionsReport, self)._run_wkhtmltopdf(
            bodies,
            report_ref=report_ref,
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
