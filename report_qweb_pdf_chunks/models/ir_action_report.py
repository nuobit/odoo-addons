# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import io
import logging
from math import ceil

from odoo import api, models

_logger = logging.getLogger(__name__)

try:
    from PyPDF2 import PdfFileMerger, PdfFileReader  # pylint: disable=W0404
except ImportError:
    _logger.debug("Can not import PyPDF2")


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


class Report(models.Model):
    _inherit = "ir.actions.report"

    @api.multi
    def render_qweb_pdf(self, res_ids=None, data=None):
        ir_config = self.env["ir.config_parameter"].sudo()
        chunk_threshold = int(
            ir_config.get_param("qweb.report.pdf.chunk.threshold", 50)
        )
        chunk_size = int(ir_config.get_param("qweb.report.pdf.chunk.size", 50))

        if (
            not res_ids
            or chunk_threshold < 0
            or len(res_ids) <= chunk_threshold
            or len(res_ids) <= chunk_size
        ):
            pdf_content, _ = super(Report, self).render_qweb_pdf(
                res_ids=res_ids, data=data
            )
        else:
            chunk_count = ceil(len(res_ids) / chunk_size)
            _logger.info(
                "Many documents to print, splitting in %i chunks of %i (max) "
                "documents each" % (chunk_count, chunk_size)
            )
            pdf_merger = PdfFileMerger()
            for i, res_ids_chunk in enumerate(chunks(res_ids, chunk_size), 1):
                _logger.info("Processing chunk %i of %i..." % (i, chunk_count))
                pdf_content_chunk, _ = super(Report, self).render_qweb_pdf(
                    res_ids=res_ids_chunk, data=data
                )

                pdf_mem_file_chunk = io.BytesIO()
                pdf_mem_file_chunk.write(pdf_content_chunk)
                pdf_chunk = PdfFileReader(pdf_mem_file_chunk)
                pdf_merger.append(pdf_chunk, import_bookmarks=False)
                pdf_mem_file_chunk.close()

            if pdf_merger:
                pdf_mem_file = io.BytesIO()
                pdf_merger.write(pdf_mem_file)
                pdf_content = pdf_mem_file.getvalue()
                pdf_mem_file.close()

        return pdf_content, "pdf"
