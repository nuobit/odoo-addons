# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AccountAsset(models.Model):
    _inherit = "account.asset"

    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Invoice",
        states={"draft": [("readonly", False)]},
        copy=False,
    )
    move_line_id = fields.Many2one(
        comodel_name="account.move.line",
        ondelete="set null",
        readonly=True,
        copy=False,
    )
