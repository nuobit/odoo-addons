# Copyright 2021 Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import calendar
import datetime

from odoo import api, fields, models


def _get_facturae_dates(date):
    _, month_days = calendar.monthrange(date.year, date.month)
    facturae_start_date = datetime.date(date.year, date.month, 1)
    facturae_end_date = datetime.date(date.year, date.month, month_days)
    return facturae_start_date, facturae_end_date


class AccountInvoice(models.Model):
    _inherit = "account.move"

    facturae_start_date = fields.Date(
        compute="_compute_facturae_dates",
        store=True,
        readonly=False,
    )
    facturae_end_date = fields.Date(
        compute="_compute_facturae_dates",
        store=True,
        readonly=False,
    )

    @api.depends("date", "facturae", "partner_id")
    def _compute_facturae_dates(self):
        for rec in self:
            partner = rec.partner_id.parent_id or rec.partner_id
            if partner:
                if rec.facturae and partner.facturae_auto_dates and rec.date:
                    (
                        rec.facturae_start_date,
                        rec.facturae_end_date,
                    ) = _get_facturae_dates(rec.date)
