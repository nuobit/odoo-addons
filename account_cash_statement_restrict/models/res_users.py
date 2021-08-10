# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    journal_id = fields.Many2one(
        "account.journal", string="Cash journal", domain=[("type", "=", "cash")]
    )
