# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
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

    allow_reprocess_bank_statement = fields.Boolean(
        compute="_compute_allow_reprocess_bank_statement"
    )

    def _compute_allow_reprocess_bank_statement(self):
        for rec in self:
            rec.allow_reprocess_bank_statement = rec.user_has_groups(
                "account_cash_statement_restrict.group_allow_reprocess_bank_statement"
            )

    def close_bank(self):
        self.write(
            {
                "state": "close",
            }
        )

    def button_reprocess(self):
        """Move the bank statements back to the 'posted' state."""
        cancelled_statements = self.filtered(lambda x: x.state == "close")
        not_cancelled_statements = self.filtered(lambda x: x.state != "close")
        super(AccountBankStatement, not_cancelled_statements).button_reprocess()
        cancelled_statements.write({"state": "posted", "date_done": False})
