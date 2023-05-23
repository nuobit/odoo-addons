# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductAttributeValueBinder(Component):
    _name = "woocommerce.product.attribute.value.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.product.attribute.value"

    external_id = "id"
    internal_id = "woocommerce_idattributevalue"

    external_alt_id = "name"
    # internal_alt_id = "default_code"
