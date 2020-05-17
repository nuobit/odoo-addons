# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, _
from odoo.exceptions import UserError


class Location(models.Model):
    _inherit = "stock.location"

    def get_putaway_strategy(self, product):
        putaway_location = super().get_putaway_strategy(product)
        if self.usage == 'view':
            return putaway_location
        current_location = self
        putaway_location = self.env['stock.location']
        while current_location and not putaway_location:
            putaway_strategy = current_location.putaway_strategy_id
            if putaway_strategy:
                putaway_location = putaway_strategy.putaway_apply(product)
                if putaway_strategy.exclude_internal_operations:
                    active_model, active_id = [
                        self.env.context.get(x) for x in ['active_model', 'active_id']]
                    if active_model in ['stock.picking.type', 'stock.picking']:
                        picking_type = self.env[active_model].browse(active_id)
                        if active_model == 'stock.picking':
                            picking_type = picking_type.picking_type_id
                    else:
                        raise UserError(_("Active model '%s' not expected") % active_model)
                    if picking_type.code == 'internal':
                        putaway_location = self.env['stock.location']
            current_location = current_location.location_id
        return putaway_location
