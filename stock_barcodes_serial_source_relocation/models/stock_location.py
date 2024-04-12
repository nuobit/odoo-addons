# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class Location(models.Model):
    _inherit = "stock.location"

    def should_bypass_reservation(self):
        if self.env.context.get("relocation"):
            return False
        return super().should_bypass_reservation()
