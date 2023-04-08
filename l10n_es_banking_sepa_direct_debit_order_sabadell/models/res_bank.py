# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class Bank(models.Model):
    _inherit = "res.bank"

    is_sabadell = fields.Boolean(string="Is Banc Sabadell", default=False)
