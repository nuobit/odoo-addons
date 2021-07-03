# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _prepare_asset_values(self):
        if self.invoice_id.date and self.invoice_id.date != self.invoice_id.date_invoice:
            self = self.with_context(update_asset_values={
                **self.env.context.get('update_asset_values', {}),
                'date': self.invoice_id.date
            })
        return super(AccountInvoiceLine, self)._prepare_asset_values()

    @api.one
    @api.depends('asset_category_id', 'invoice_id.date_invoice', 'invoice_id.date')
    def _get_asset_date(self):
        super(AccountInvoiceLine, self)._get_asset_date()
        cat = self.asset_category_id
        if cat:
            months = cat.method_number * cat.method_period
            if self.invoice_id.date and self.invoice_id.date != self.invoice_id.date_invoice:
                start_date = datetime.strptime(self.invoice_id.date, DF).replace(day=1)
                end_date = (start_date + relativedelta(months=months, days=-1))
                self.asset_start_date = start_date.strftime(DF)
                self.asset_end_date = end_date.strftime(DF)
