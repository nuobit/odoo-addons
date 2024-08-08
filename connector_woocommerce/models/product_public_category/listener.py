# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductPublicCategoryListener(Component):
    _name = "woocommerce.product.public.category.listener"
    _inherit = "connector.extension.event.listener"

    _apply_on = "product.public.category"