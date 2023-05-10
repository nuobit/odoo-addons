# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductPublicCategoryBinder(Component):
    _name = "woocommerce.product.public.category.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.product.public.category"

    external_id = "id"
    internal_id = "woocommerce_idproduct"

    external_alt_id = "name"
