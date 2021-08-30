# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Location(models.Model):
    _inherit = "stock.location"

    posx = fields.Char("Corridor (X)", default=None)
    posy = fields.Char("Shelves (Y)", default=None)
    posz = fields.Char("Height (Z)", default=None)
