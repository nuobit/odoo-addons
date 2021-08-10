# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    state = fields.Selection(
        selection=[("open", "New"), ("close", "Closed"), ("confirm", "Validated")]
    )

    @api.multi
    def close_bank(self, vals):
        for rec in self:
            rec.state = "close"
