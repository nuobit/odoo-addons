# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, _


class Location(models.Model):
    _inherit = "stock.location"

    def get_putaway_strategy(self, product):
        super().get_putaway_strategy(product)
        current_location = self
        putaway_location = self.env['stock.location']
        while current_location and not putaway_location:
            putaway_strategy = current_location.putaway_strategy_id
            if putaway_strategy:
                putaway_location = putaway_strategy.putaway_apply(product)
                if putaway_strategy.exclude_internal_operations:
                    stock_picking_type = self.env['stock.picking.type'].browse(
                        self.env.context.get('active_id'))
                    if stock_picking_type.code == 'internal':
                        putaway_location = self.env['stock.location']
            current_location = current_location.location_id
        return putaway_location
