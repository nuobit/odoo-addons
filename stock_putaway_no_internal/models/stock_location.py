# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import UserError


class Location(models.Model):
    _inherit = "stock.location"

    def _excluded_picking_types(self):
        return ["internal"]

    def get_putaway_strategy(self, product):
        putaway_location = super().get_putaway_strategy(product)
        if self.usage == "view":
            return putaway_location
        current_location = self
        putaway_location = self.env["stock.location"]
        while current_location and not putaway_location:
            putaway_strategy = current_location.putaway_strategy_id
            if putaway_strategy:
                putaway_location = putaway_strategy.putaway_apply(product)
                if putaway_strategy.exclude_internal_operations:
                    picking_type_code = self.env.context.get("stock_picking_type_code")
                    if not picking_type_code:
                        raise UserError(_("No picking type defined in context"))
                    if picking_type_code in self._excluded_picking_types():
                        putaway_location = self.env["stock.location"]
            current_location = current_location.location_id
        return putaway_location
