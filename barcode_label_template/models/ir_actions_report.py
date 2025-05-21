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
    def _get_report(self, report_ref):
        """Override to set the watermark on the report."""
        report = super()._get_report(report_ref)
        if report:
            templ_config_id = self.env.context.get("template_configuration_id")
            if templ_config_id:
                temp_config = (
                    self.env["barcode.label.template.configuration"]
                    .browse(templ_config_id)
                    .exists()
                )
                if temp_config:
                    report.pdf_watermark = temp_config.template
        return report
