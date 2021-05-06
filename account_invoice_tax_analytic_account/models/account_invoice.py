# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging
from ast import literal_eval

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def get_taxes_values(self):
        res = super(AccountInvoice, self).get_taxes_values()
        for key in res.keys():
            (
                res[key]["origin_account_analytic_id"],
                res[key]["origin_analytic_tag_ids"],
            ) = [x and literal_eval(x) or False for x in key.split("-")][-2:]
        return res

    def _prepare_tax_line_vals(self, line, tax):
        vals = super(AccountInvoice, self)._prepare_tax_line_vals(line, tax)
        # If the taxes generate moves on the same financial account
        # as the invoice line, propagate the analytic tags from the invoice
        # line to the tax line. This is necessary in situations were (part of)
        # the taxes cannot be reclaimed, to ensure the tax move is allocated
        # to the proper analytic account tags.
        if (
            not vals.get("analytic_tag_ids")
            and line.analytic_tag_ids
            and vals["account_id"] == line.account_id.id
        ):
            vals["analytic_tag_ids"] = line.analytic_tag_ids.ids
        return vals


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    origin_account_analytic_id = fields.Many2one(
        "account.analytic.account", string="Analytic account Origin"
    )
    origin_analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        relation="account_invoice_origin_analytic_tag_rel",
        column1="invoice_id",
        column2="tag_id",
        string="Analytic tags Origin",
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
                        "analytic_tag_ids": tax.origin_analytic_tag_ids.ids or False,
                    }
                )
                if tax.invoice_id and key in tax_grouped[tax.invoice_id.id]:
                    tax.base = tax_grouped[tax.invoice_id.id][key]["base"]
                else:
                    _logger.warning(
                        "Tax Base Amount not computable probably due to a change "
                        "in an underlying tax (%s).",
                        tax.tax_id.name,
                    )
