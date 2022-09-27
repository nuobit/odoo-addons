# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AccountAsset(models.Model):
    _inherit = "account.asset"

    invoice_number = fields.Char(string="Invoice Number")
    invoice_date = fields.Date(string="Invoice Date")
    tax_base_amount = fields.Monetary(string="Tax Base Amount")

    tax_ids = fields.Many2many(
        comodel_name="account.tax",
        string="Taxes",
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="move_line_id.currency_id",
        string="Currency",
    )
