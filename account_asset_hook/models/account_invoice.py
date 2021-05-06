# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _prepare_asset_values(self):
        vals = {
            'name': self.name,
            'code': self.invoice_id.number or False,
            'category_id': self.asset_category_id.id,
            'value': self.price_subtotal_signed,
            'partner_id': self.invoice_id.partner_id.id,
            'company_id': self.invoice_id.company_id.id,
            'currency_id': self.invoice_id.company_currency_id.id,
            'date': self.invoice_id.date_invoice,
            'invoice_id': self.invoice_id.id,
        }
        vals.update(self.env.context.get('update_asset_values', {}))
        changed_vals = self.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
        vals.update(changed_vals['value'])
        return vals

    @api.one
    def asset_create(self):
        if self.asset_category_id:
            vals = self._prepare_asset_values()
            asset = self.env['account.asset.asset'].create(vals)
            if self.asset_category_id.open_asset:
                asset.validate()
        return True

    def _check_null_depreciations(self, cat):
        if cat.method_number == 0 or cat.method_period == 0:
            raise UserError(
                _('The number of depreciations or the period length of your asset category cannot be null.'))
        return True

    @api.one
    @api.depends('asset_category_id', 'invoice_id.date_invoice')
    def _get_asset_date(self):
        self.asset_mrr = 0
        self.asset_start_date = False
        self.asset_end_date = False
        cat = self.asset_category_id
        if cat:
            self._check_null_depreciations(cat)
            months = cat.method_number * cat.method_period
            if self.invoice_id.type in ['out_invoice', 'out_refund']:
                self.asset_mrr = self.price_subtotal_signed / months
            if self.invoice_id.date_invoice:
                start_date = datetime.strptime(self.invoice_id.date_invoice, DF).replace(day=1)
                end_date = (start_date + relativedelta(months=months, days=-1))
                self.asset_start_date = start_date.strftime(DF)
                self.asset_end_date = end_date.strftime(DF)