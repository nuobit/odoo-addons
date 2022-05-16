# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        for rec in self:
            super(AccountMove, rec)._post(soft=soft)
            self._event("on_validate_invoice").notify(rec)

    def button_draft(self):
        for rec in self:
            super(AccountMove, rec).button_draft()
            self._event("on_cancel_invoice").notify(rec)
