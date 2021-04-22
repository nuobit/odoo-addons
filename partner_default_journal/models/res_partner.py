# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_journal_id = fields.Many2one(
        "account.journal", "Default Sale journal", domain=[("type", "=", "sale")]
    )
    purchase_journal_id = fields.Many2one(
        "account.journal",
        "Default Purchase journal",
        domain=[("type", "=", "purchase")],
    )
