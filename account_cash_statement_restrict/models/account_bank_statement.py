# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    state = fields.Selection(
        selection_add=[
            ("close", "Closed"),
        ],
        ondelete={"close": lambda recs: recs.write({"state": "open"})},
    )

    def close_bank(self):
        self.write(
            {
                "state": "close",
            }
        )
