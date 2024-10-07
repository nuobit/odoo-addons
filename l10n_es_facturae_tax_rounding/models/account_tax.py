# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools.float_utils import float_round


class AccountTax(models.Model):
    _inherit = "account.tax"

    def get_tax_amount(self, amount, currency, company):
        self.ensure_one()
        tax_amount = amount * self.amount / 100
        prec = currency.rounding
        if company.tax_calculation_rounding_method == "round_globally":
            prec *= 1e-5
        tax_amount = float_round(tax_amount, precision_rounding=prec)
        return tax_amount
