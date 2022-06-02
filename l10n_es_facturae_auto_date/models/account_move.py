# Copyright 2021 Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import calendar
import datetime

from odoo import api, fields, models


def _get_facturae_dates(invoice_date):
    if isinstance(invoice_date, str):
        invoice_date = fields.Date.from_string(invoice_date)
    _, month_days = calendar.monthrange(invoice_date.year, invoice_date.month)
    facturae_start_date = datetime.date(invoice_date.year, invoice_date.month, 1)
    facturae_end_date = datetime.date(invoice_date.year, invoice_date.month, month_days)
    return facturae_start_date, facturae_end_date


class AccountInvoice(models.Model):
    _inherit = "account.move"

    @api.onchange("invoice_date")
    def _onchange_auto_date_invoice_date(self):
        partner_id = self.partner_id.parent_id or self.partner_id
        if self.facturae and self.invoice_date and partner_id.facturae_auto_dates:
            self.facturae_start_date, self.facturae_end_date = _get_facturae_dates(
                self.invoice_date
            )
        else:
            self.facturae_start_date = False
            self.facturae_end_date = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            partner_id = vals.get("partner_id")
            if partner_id:
                partner = self.env["res.partner"].browse(partner_id)
                partner = partner.parent_id or partner
                facturae = vals.get("facturae", partner.facturae)
                auto_date = vals.get("facturae_auto_dates", partner.facturae_auto_dates)
                if facturae and auto_date:
                    invoice_date = vals.get("invoice_date")
                    if invoice_date:
                        if (
                            vals.get("facturae_start_date") is not False
                            and vals.get("facturae_end_date") is not False
                        ):
                            (
                                vals["facturae_start_date"],
                                vals["facturae_end_date"],
                            ) = _get_facturae_dates(invoice_date)
        return super(AccountInvoice, self).create(vals_list)

    def write(self, vals):
        for rec in self:
            facturae = vals.get("facturae", rec.facturae)
            auto_date = vals.get(
                "facturae_auto_dates",
                (rec.partner_id.parent_id or rec.partner_id).facturae_auto_dates,
            )
            if facturae and auto_date:
                invoice_date = vals.get("invoice_date")
                if invoice_date is not None:
                    if (
                        vals.get("facturae_start_date") is not False
                        and vals.get("facturae_end_date") is not False
                    ):
                        if invoice_date:
                            (
                                vals["facturae_start_date"],
                                vals["facturae_end_date"],
                            ) = _get_facturae_dates(invoice_date)
                        else:
                            vals["facturae_start_date"], vals["facturae_end_date"] = (
                                False,
                                False,
                            )
        return super(AccountInvoice, self).write(vals)
