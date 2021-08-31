# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class Location(models.Model):
    _inherit = "stock.location"

    def _excluded_picking_types(self):
        return super(Location, self)._excluded_picking_types() + ["mrp_operation"]
