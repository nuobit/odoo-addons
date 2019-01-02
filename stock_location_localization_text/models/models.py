# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class Location(models.Model):
    _inherit = "stock.location"

    posx = fields.Char(default=None)
    posy = fields.Char(default=None)
    posz = fields.Char(default=None)
