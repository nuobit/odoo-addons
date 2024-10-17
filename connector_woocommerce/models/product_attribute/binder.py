# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductAttributeBinder(Component):
    _name = "woocommerce.product.attribute.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.product.attribute"

    @property
    def external_id(self):
        return ["id"]

    @property
    def internal_id(self):
        return ["woocommerce_idattribute"]

    @property
    def external_alt_id(self):
        return ["name"]
