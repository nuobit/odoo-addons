# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductAttributeValueBinder(Component):
    _name = "woocommerce.product.attribute.value.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.product.attribute.value"

    # TODO: Review: Parent_id is a required field to search but if we try
    #  to rebind we need export parents(attributes) before
    @property
    def external_id(self):
        return ["parent_id", "id"]

    @property
    def internal_id(self):
        return ["woocommerce_idattribute", "woocommerce_idattributevalue"]

    @property
    def external_alt_id(self):
        return ["parent_name", "name"]
