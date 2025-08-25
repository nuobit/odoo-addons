# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductTemplateBinder(Component):
    _name = "woocommerce.product.template.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.product.template"

    @property
    def external_id(self):
        return ["id"]

    @property
    def internal_id(self):
        return ["woocommerce_idproduct"]

    @property
    def external_alt_id(self):
        return ["sku"]

    @property
    def internal_alt_id(self):
        return ["default_code"]
