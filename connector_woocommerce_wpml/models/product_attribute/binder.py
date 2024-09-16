# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceWPMLProductAttributeBinder(Component):
    _name = "woocommerce.wpml.product.attribute.binder"
    _inherit = "woocommerce.wpml.binder"

    _apply_on = "woocommerce.wpml.product.attribute"

    external_id = ["id"]
    internal_id = ["woocommerce_wpml_idattribute"]
    external_alt_id = ["name"]
