# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("invoice_date", "highest_name", "company_id")
    def _onchange_invoice_date(self):
        super()._onchange_invoice_date()
        if self.line_ids.tax_ids.filtered("prorate"):
            self._recompute_dynamic_lines(
                recompute_all_taxes=True, recompute_tax_base_amount=True
            )
