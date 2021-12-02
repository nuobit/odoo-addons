# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_invoice_open(self):
        res = True
        for rec in self:
            res &= super(AccountInvoice, rec).action_invoice_open()
            self._event("on_validate_invoice").notify(rec)

        return res

    @api.multi
    def action_invoice_cancel(self):
        res = True
        for rec in self:
            res &= super(AccountInvoice, rec).action_invoice_cancel()
            self._event("on_cancel_invoice").notify(rec)

        return res
