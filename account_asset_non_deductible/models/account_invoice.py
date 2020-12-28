# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _get_asset_base_value(self):
        super(AccountInvoiceLine, self)._get_asset_base_value()
        value = self.price_subtotal_signed
        tax_non_deductible_percent = \
            self.invoice_line_tax_ids.get_non_deductible_percent(
                self.invoice_id.date or self.invoice_id.date_invoice,
                self.invoice_id.company_id.id or self.env.user.company_id.id
            )
        if tax_non_deductible_percent:
            value += round(value * tax_non_deductible_percent / 100,
                           self.currency_id.decimal_places)
        return value
