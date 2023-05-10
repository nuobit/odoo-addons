# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class WooCommerceSaleOrderExportMapper(Component):
    _name = "woocommerce.sale.order.export.mapper"
    _inherit = "woocommerce.export.mapper"

    _apply_on = "woocommerce.sale.order"

    # def get_picking_status(self, state):
    #     if state == 'draft':
    #         return 'checkout-draft'
    #     elif state == 'waiting':
    #         return 'on-hold'
    #     elif state == 'confirmed':
    #         return 'on-hold'
    #     elif state == 'assigned':
    #         return 'processing'
    #     elif state == 'done':
    #         return 'completed'
    #     elif state == 'cancel':
    #         return 'cancelled'

    @mapping
    def status(self, record):
        a=1
        for line in record.order_line:
            linestate=line.website_line_state
            a=1

        if record.picking_ids:
            status = 'completed'
            if len(record.picking_ids) == 1:
                status = self.get_picking_status(record.picking_ids.state)
            else:
                states = record.picking_ids.mapped('state')
                if len(states) == 1:
                    self.get_picking_status(states)
        else:
            if record.state == 'draft':
                status = 'Checkout-draft'
            elif record.state == 'cancel':
                status = 'cancelled'
            elif record.state == 'sale':
                status = 'pending'
            elif record.state == 'sent':
                status = 'pending'
            # TODO: si el product es service, podria ser el done com a completed?
            # elif record.state == 'done':
            #     status = 'pending'

        return {"status": status}
