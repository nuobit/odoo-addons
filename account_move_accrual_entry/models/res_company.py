# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    accrual_account_id = fields.Many2one(
        comodel_name="account.account",
    )

    accrual_account_asset_type_id = fields.Many2one(
        comodel_name="account.account.type",
        default=lambda self: self.env.ref("account.data_account_type_fixed_assets"),
    )
