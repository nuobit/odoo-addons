# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductAttributeValueBinder(Component):
    _name = "woocommerce.product.attribute.value.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.product.attribute.value"

    external_id = ["parent_id", "id"]
    internal_id = ["woocommerce_idattribute", "woocommerce_idattributevalue"]

    external_alt_id = ["parent_name", "name"]
