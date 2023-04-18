# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    cege = fields.Char(
        string="Cege",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
