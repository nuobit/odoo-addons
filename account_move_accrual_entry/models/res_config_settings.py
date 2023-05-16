# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    accrual_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.accrual_account_id",
        readonly=False,
        domain=[
            ("reconcile", "=", True),
            ("deprecated", "=", False),
            ("user_type_id.type", "not in", ("receivable", "payable")),
            ("is_off_balance", "=", False),
        ],
    )

    accrual_account_asset_type_id = fields.Many2one(
        comodel_name="account.account.type",
        related="company_id.accrual_account_asset_type_id",
        readonly=False,
        domain=[("internal_group", "=", "asset")],
    )
