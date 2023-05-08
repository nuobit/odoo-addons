# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    accrual_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Accrual Account",
        related="company_id.accrual_account_id",
        readonly=False,
        domain=[
            ("reconcile", "=", True),
            ("deprecated", "=", False),
            ("user_type_id.type", "not in", ("receivable", "payable")),
            ("is_off_balance", "=", False),
        ],
    )

    accrual_asset_account_type_id = fields.Many2one(
        comodel_name="account.account.type",
        string="Account Type for Assets",
        related="company_id.accrual_asset_account_type_id",
        readonly=False,
        domain=[("internal_group", "=", "asset")],
    )
