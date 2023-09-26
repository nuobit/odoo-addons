# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceSaleOrderListener(Component):
    _inherit = "sale.order.listener"

    def _get_fields_to_update(self):
        fields_to_update = super()._get_fields_to_update()
        fields_to_update.add("woocommerce_ast_fields")
        return fields_to_update
