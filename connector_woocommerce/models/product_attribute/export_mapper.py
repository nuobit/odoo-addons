# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class WooCommerceProductAttributeExportMapper(Component):
    _name = "woocommerce.product.attribute.export.mapper"
    _inherit = "woocommerce.export.mapper"

    _apply_on = "woocommerce.product.attribute"

    @changed_by("name")
    @mapping
    def name(self, record):
        return {
            "name": record.with_context(lang=self.backend_record.language_id.code).name
        }
