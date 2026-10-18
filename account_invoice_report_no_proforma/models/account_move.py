# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_invoice_proforma_pdf_report_filename(self):
        return (
            self._get_invoice_report_filename()
            if self.state == "posted"
            else super()._get_invoice_proforma_pdf_report_filename()
        )
