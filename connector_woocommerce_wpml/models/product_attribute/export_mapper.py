# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class WooCommerceWPMLProductAttributeExportMapper(Component):
    _name = "woocommerce.wpml.product.attribute.export.mapper"
    _inherit = "woocommerce.wpml.export.mapper"

    _apply_on = "woocommerce.wpml.product.attribute"

    @changed_by("name")
    @mapping
    def name(self, record):
        return {"name": record.name}
