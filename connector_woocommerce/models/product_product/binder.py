# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductProductBinder(Component):
    _name = "woocommerce.product.product.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.product.product"

    external_id = ["parent_id", "id"]
    internal_id = ["woocommerce_idparent", "woocommerce_idproduct"]

    external_alt_id = "sku"
    internal_alt_id = "default_code"
