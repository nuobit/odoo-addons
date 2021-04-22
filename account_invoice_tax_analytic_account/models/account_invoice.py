# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def get_taxes_values(self):
        res = super(AccountInvoice, self).get_taxes_values()

        bmap = {"False": False, "True": True}
        for key, tax in res.items():
            _, _, res[key]["origin_account_analytic_id"] = [
                x not in bmap and int(x) or bmap[x] for x in key.split("-")
            ]

        return res


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    origin_account_analytic_id = fields.Many2one(
        "account.analytic.account", string="Analytic account Origin"
    )

    def _compute_base_amount(self):
        super(AccountInvoiceTax, self)._compute_base_amount()
        tax_grouped = {}
        for invoice in self.mapped("invoice_id"):
            tax_grouped[invoice.id] = invoice.get_taxes_values()
        for tax in self:
            tax.base = 0.0
            if tax.tax_id:
                key = tax.tax_id.get_grouping_key(
                    {
                        "tax_id": tax.tax_id.id,
                        "account_id": tax.account_id.id,
                        "account_analytic_id": tax.origin_account_analytic_id.id,
                    }
                )
                if tax.invoice_id and key in tax_grouped[tax.invoice_id.id]:
                    tax.base = tax_grouped[tax.invoice_id.id][key]["base"]
                else:
                    _logger.warning(
                        "Tax Base Amount not computable probably due to a change in an underlying tax (%s).",
                        tax.tax_id.name,
                    )
