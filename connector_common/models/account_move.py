# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        for rec in self:
            super(AccountMove, rec).action_post()
            self._event("on_validate_invoice").notify(rec)

    def button_draft(self):
        for rec in self:
            super(AccountMove, rec).button_draft()
            self._event("on_cancel_invoice").notify(rec)
