# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SaleOrderBinder(Component):
    _name = 'veloconnect.sale.order.binder'
    _inherit = 'veloconnect.binder'

    _apply_on = 'veloconnect.sale.order'

    # _external_field = ['marketplace', 'marketplace_order_id']
    # _internal_field = ['veloconnect_marketplace', 'veloconnect_marketplace_order_id']
