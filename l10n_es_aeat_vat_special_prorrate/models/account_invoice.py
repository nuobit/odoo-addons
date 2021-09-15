# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("invoice_date", "date")
    def _onchange_dates(self):
        self._onchange_invoice_line_ids()

    def _preprocess_taxes_map(self, taxes_map):
        tax_grouped = super()._preprocess_taxes_map(taxes_map)
        prec = self.currency_id.decimal_places
        for tax_d in tax_grouped.values():
            tax = self.env["account.tax"].browse(tax_d["tax_id"])
            if tax.prorrate_type:
                if tax.amount_type == "percent" and not tax.price_include:
                    base_amount = tax_d["base"] * tax.get_prorrate_ratio(
                        self.date or self.invoice_date,
                        self.company_id.id or self.env.company.id,
                    )
                    tax_d["base"] = round(base_amount, prec)
                    tax_d["amount"] = round(base_amount * tax.amount / 100, prec)
                else:
                    raise ValidationError(
                        _("Only suported 'percent' type with price not included")
                    )
        return tax_grouped
