# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductPublicCategoryExportMapper(Component):
    _name = "woocommerce.product.public.category.export.mapper"
    _inherit = "woocommerce.export.mapper"

    _apply_on = "woocommerce.product.public.category"

    direct = [
        ("name", "name"),
    ]
