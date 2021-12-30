# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AccountAnalyticContractLine(models.Model):
    _inherit = "account.analytic.contract.line"

    tax_ids = fields.Many2many(
        comodel_name="account.tax",
        string="Taxes",
        domain=[
            ("type_tax_use", "!=", "none"),
            "|",
            ("active", "=", False),
            ("active", "=", True),
        ],
    )
