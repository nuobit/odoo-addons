# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models
import logging

_logger = logging.getLogger(__name__)


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    def _compute_base_amount(self):
        tax_grouped = {}
        for invoice in self.mapped('invoice_id'):
            tax_grouped[invoice.id] = invoice.get_taxes_values()
        for tax in self:
            tax.base = 0.0
            if tax.tax_id:
                if tax.tax_id.analytic:
                    account_analytic_id = tax.account_analytic_id.id
                else:
                    account_analytic_id = False
                key = tax.tax_id.get_grouping_key({
                    'tax_id': tax.tax_id.id,
                    'account_id': tax.account_id.id,
                    'account_analytic_id': account_analytic_id,
                })
                if tax.invoice_id and key in tax_grouped[tax.invoice_id.id]:
                    tax.base = tax_grouped[tax.invoice_id.id][key]['base']
                else:
                    _logger.warning(
                        'Tax Base Amount not computable probably due to a change in an underlying tax (%s).',
                        tax.tax_id.name)
