# Copyright 2021 Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import calendar
import datetime

from odoo import fields, api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_facturae_dates(self, date_invoice):
        date_invoice = fields.Date.from_string(date_invoice)
        _, month_days = calendar.monthrange(date_invoice.year, date_invoice.month)
        facturae_start_date = fields.Date.to_string(
            datetime.date(date_invoice.year, date_invoice.month, 1)
        )
        facturae_end_date = fields.Date.to_string(
            datetime.date(date_invoice.year, date_invoice.month, month_days)
        )
        return facturae_start_date, facturae_end_date

    @api.onchange('date_invoice')
    def onchange_date_invoice(self):
        if self.facturae and self.date_invoice:
            self.facturae_start_date, self.facturae_end_date = \
                self._get_facturae_dates(self.date_invoice)
        else:
            self.facturae_start_date = False
            self.facturae_end_date = False

    @api.model
    def create(self, vals):
        if not vals.get('facturae_start_date') and not vals.get('facturae_end_date'):
            facturae, date_invoice = vals.get('facturae'), vals.get('date_invoice')
            if facturae and date_invoice:
                facturae_start_date, facturae_end_date = \
                    self._get_facturae_dates(date_invoice)
                vals.update({
                    'facturae_start_date': facturae_start_date,
                    'facturae_end_date': facturae_end_date,
                })
        return super(AccountInvoice, self).create(vals)

    def write(self, vals):
        for rec in self:
            facturae = vals.get('facturae', rec.facturae)
            if facturae:
                if not vals.get('facturae_start_date') and not vals.get('facturae_end_date'):
                    facturae_start_date, facturae_end_date = False, False
                    date_invoice = vals.get('date_invoice', rec.date_invoice)
                    if date_invoice:
                        facturae_start_date, facturae_end_date = \
                            self._get_facturae_dates(date_invoice)
                    vals1 = {}
                    if rec.facturae_start_date != facturae_start_date:
                        vals1['facturae_start_date'] = facturae_start_date
                    if rec.facturae_end_date != facturae_end_date:
                        vals1['facturae_end_date'] = facturae_end_date
                    if vals1:
                        super(AccountInvoice, rec).write(vals1)

        return super(AccountInvoice, self).write(vals)
