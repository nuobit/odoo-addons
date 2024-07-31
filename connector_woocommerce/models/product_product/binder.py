# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductProductBinder(Component):
    _name = "woocommerce.product.product.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.product.product"

    @property
    def external_id(self):
        return ["parent_id", "id"]

    @property
    def internal_id(self):
        return ["woocommerce_idparent", "woocommerce_idproduct"]

    @property
    def external_alt_id(self):
        return ["sku"]

    @property
    def internal_alt_id(self):
        return ["default_code"]
