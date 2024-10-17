# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductPublicCategoryBinder(Component):
    _name = "woocommerce.product.public.category.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.product.public.category"

    @property
    def external_id(self):
        return ["id"]

    @property
    def internal_id(self):
        return ["woocommerce_idpubliccategory"]

    @property
    def external_alt_id(self):
        return ["name"]
