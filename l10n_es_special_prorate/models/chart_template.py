# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models

from . import account_tax_mixin


class AccountTaxTemplate(models.Model):
    _inherit = "account.tax.template"

    prorate = fields.Boolean(string="Prorate")

    @api.constrains(
        "prorate",
        "amount_type",
        "type_tax_use",
        "invoice_repartition_line_ids",
        "refund_repartition_line_ids",
    )
    def _check_prorate(self):
        account_tax_mixin.check_prorate(self)

    def _get_tax_vals(self, company, tax_template_to_tax):
        return {
            **super()._get_tax_vals(company, tax_template_to_tax),
            "prorate": self.prorate,
        }
