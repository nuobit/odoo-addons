# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class Location(models.Model):
    _inherit = "stock.location"

    def _get_putaway_strategy(self, product):
        putaway_location = super()._get_putaway_strategy(product)
        if self.usage == "view":
            return putaway_location
        current_location = self
        putaway_location = self.env["stock.location"]
        while current_location and not putaway_location:
            putaway_rules = current_location.putaway_rule_ids.filtered(
                lambda x: x.product_id == product
            )
            if putaway_rules:
                putaway_location = putaway_rules[0].location_out_id
            else:
                categ = product.categ_id
                while categ:
                    putaway_rules = current_location.putaway_rule_ids.filtered(
                        lambda x: x.category_id == categ
                    )
                    if putaway_rules:
                        putaway_location = putaway_rules[0].location_out_id
                        break
                    categ = categ.parent_id
            if putaway_rules:
                location_dest = self.env.context.get("stock_location_dest", False)
                if location_dest and not location_dest.child_ids:
                    putaway_location = self.env["stock.location"]
            current_location = current_location.location_id
        return putaway_location
