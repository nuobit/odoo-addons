# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    repair_order_id = fields.Many2one(
        comodel_name="repair.order",
        string="Repair Order",
        ondelete="restrict",
        help="The repair order related to this invoice",
    )
