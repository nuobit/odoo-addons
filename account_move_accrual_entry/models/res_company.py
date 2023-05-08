# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    accrual_account_id = fields.Many2one(
        comodel_name="account.account", string="Accrual Account"
    )

    accrual_asset_account_type_id = fields.Many2one(
        comodel_name="account.account.type", string="Account Type for Assets"
    )
