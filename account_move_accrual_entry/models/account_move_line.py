# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    accrual_date = fields.Date(related="move_id.accrual_date", readonly=True)
    accrual_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Accrual Account",
    )

    @api.onchange("account_id")
    def _onchange_accrual_entry_account_id(self):
        for line in self:
            if (
                line.move_id.move_type in ("out_invoice", "out_refund")
                and line.move_id.accrual_date
            ):
                if not line.accrual_account_id:
                    line.accrual_account_id = line.account_id
                else:
                    line.accrual_account_id = super(
                        AccountMoveLine, line
                    )._get_computed_account()
                line.account_id = line.move_id.company_accrual_account_id
            else:
                line.accrual_account_id = False
