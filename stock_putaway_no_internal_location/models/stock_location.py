# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class Location(models.Model):
    _inherit = "stock.location"

    def _excluded_location_usages(self):
        return ["internal"]

    def _get_putaway_strategy(self, product):
        putaway_location = super()._get_putaway_strategy(product)
        if self.usage in self._excluded_location_usages():
            return self
        return putaway_location
