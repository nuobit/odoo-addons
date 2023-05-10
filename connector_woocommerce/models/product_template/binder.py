# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductTemplateBinder(Component):
    _name = "woocommerce.product.template.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.product.template"

    external_id = "id"
    internal_id = "woocommerce_idproduct"

    external_alt_id = "sku"
    internal_alt_id = "default_code"
