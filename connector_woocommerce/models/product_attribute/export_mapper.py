# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductAttributeExportMapper(Component):
    _name = "woocommerce.product.attribute.export.mapper"
    _inherit = "woocommerce.export.mapper"

    _apply_on = "woocommerce.product.attribute"
    direct = [
        ("name", "name"),
    ]
