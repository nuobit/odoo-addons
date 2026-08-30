# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("invoice_date")
    def _onchange_invoice_date_prorate(self):
        if self.line_ids.tax_ids.filtered("prorate"):
            AccountTax = self.env["account.tax"]
            base_lines, tax_lines = self._get_rounded_base_and_tax_lines(
                round_from_tax_lines=False
            )
            AccountTax._add_accounting_data_in_base_lines_tax_details(
                base_lines,
                self.company_id,
                include_caba_tags=self.always_tax_exigible,
            )
            tax_results = AccountTax._prepare_tax_lines(
                base_lines,
                self.company_id,
                tax_lines=tax_lines,
            )
            for tax_vals, _key, to_update in tax_results["tax_lines_to_update"]:
                tax_vals["record"].update(to_update)
