# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SaleOrderBinder(Component):
    _name = "lengow.sale.order.binder"
    _inherit = "lengow.binder"

    _apply_on = "lengow.sale.order"

    external_id = ["marketplace", "marketplace_order_id"]
    internal_id = ["lengow_marketplace", "lengow_marketplace_order_id"]
