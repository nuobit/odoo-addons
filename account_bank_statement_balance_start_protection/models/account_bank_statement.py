# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    disable_balance_start = fields.Boolean()  # compute="_disable_balance_start")

    @api.model
    def create(self, vals):
        vals.update({"disable_balance_start": True})
        result = super().create(vals)
        return result

    @api.multi
    def write(self, vals):
        vals.update({"disable_balance_start": True})
        result = super().write(vals)
        return result
