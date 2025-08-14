# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("invoice_date")
    def _onchange_invoice_date_accounting(self):
        self.date = self.invoice_date
