# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_invoice_open(self):
        res = True
        for rec in self:
            res &= super(AccountMove, rec).action_invoice_open()
            self._event("on_validate_invoice").notify(rec)

        return res

    def action_invoice_cancel(self):
        res = True
        for rec in self:
            res &= super(AccountMove, rec).action_invoice_cancel()
            self._event("on_cancel_invoice").notify(rec)

        return res
