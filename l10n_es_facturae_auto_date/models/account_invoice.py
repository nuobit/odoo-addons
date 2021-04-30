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
        partner_id = self.partner_id.parent_id or self.partner_id
        if self.facturae and self.date_invoice and partner_id.facturae_auto_dates:
            self.facturae_start_date, self.facturae_end_date = \
                self._get_facturae_dates(self.date_invoice)
        else:
            self.facturae_start_date = False
            self.facturae_end_date = False

    @api.model
    def create(self, vals):
        partner_id = vals.get('partner_id')
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            partner = partner.parent_id or partner
            facturae = vals.get('facturae', partner.facturae)
            auto_date = vals.get('facturae_auto_dates', partner.facturae_auto_dates)
            if facturae and auto_date:
                date_invoice = vals.get('date_invoice')
                if date_invoice:
                    if vals.get('facturae_start_date') != False and vals.get('facturae_end_date') != False:
                        vals['facturae_start_date'], vals['facturae_end_date'] = \
                            self._get_facturae_dates(date_invoice)

        return super(AccountInvoice, self).create(vals)

    @api.multi
    def write(self, vals):
        for rec in self:
            facturae = vals.get('facturae', rec.facturae)
            auto_date = vals.get('facturae_auto_dates',
                                 (rec.partner_id.parent_id or rec.partner_id).facturae_auto_dates)
            if facturae and auto_date:
                date_invoice = vals.get('date_invoice')
                if date_invoice is not None:
                    if vals.get('facturae_start_date') != False and vals.get('facturae_end_date') != False:
                        if date_invoice:
                            vals['facturae_start_date'], vals['facturae_end_date'] = \
                                self._get_facturae_dates(date_invoice)
                        else:
                            vals['facturae_start_date'], vals['facturae_end_date'] = False, False

        return super(AccountInvoice, self).write(vals)
