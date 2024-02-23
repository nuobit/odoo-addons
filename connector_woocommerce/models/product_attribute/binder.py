# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductAttributeBinder(Component):
    _name = "woocommerce.product.attribute.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.product.attribute"

    external_id = "id"
    internal_id = "woocommerce_idattribute"

    external_alt_id = "name"
