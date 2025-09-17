# Copyright NuoBiT Solutions SL - Frank Cespedes <fcespedes@nuobit.com>
# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    accrual_account_id = fields.Many2one(
        comodel_name="account.account",
        domain=[
            ("reconcile", "=", True),
            ("deprecated", "=", False),
            ("account_type", "not in", ("receivable", "payable")),
            ("internal_group", "!=", "off"),
        ],
    )

    accrual_journal_id = fields.Many2one(
        comodel_name="account.journal",
        domain=[("type", "=", "general")],
    )

    accrual_account_asset_type_id = fields.Many2one(
        comodel_name="account.account",
        default=lambda self: self.env["account.account"].search(
            [("account_type", "=", "asset_fixed")], limit=1
        ),
        domain=[("internal_group", "=", "asset")],
    )
