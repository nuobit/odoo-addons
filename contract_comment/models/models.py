# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    comment = fields.Text("Additional Information")

    @api.multi
    def _prepare_invoice(self):
        invoice = super()._prepare_invoice()

        invoice.update({"comment": self.comment})

        return invoice
