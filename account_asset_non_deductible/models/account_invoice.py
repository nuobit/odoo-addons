# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.one
    def asset_create(self):
        if self.asset_category_id:
            value = self.price_subtotal_signed

            tax_non_deductible_percent = \
                self.invoice_line_tax_ids._get_non_deductible_percent(
                    self.invoice_id.date or self.invoice_id.date_invoice,
                    self.invoice_id.company_id or self.env.user.company_id
                )
            if tax_non_deductible_percent:
                value += round(value * tax_non_deductible_percent / 100,
                               self.currency_id.decimal_places)

            vals = {
                'name': self.name,
                'code': self.invoice_id.number or False,
                'category_id': self.asset_category_id.id,
                'value': value,
                'partner_id': self.invoice_id.partner_id.id,
                'company_id': self.invoice_id.company_id.id,
                'currency_id': self.invoice_id.company_currency_id.id,
                'date': self.invoice_id.date_invoice,
                'invoice_id': self.invoice_id.id,
            }
            changed_vals = self.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
            vals.update(changed_vals['value'])
            asset = self.env['account.asset.asset'].create(vals)
            if self.asset_category_id.open_asset:
                asset.validate()
        return True
