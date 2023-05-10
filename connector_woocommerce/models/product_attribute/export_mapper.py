# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


def nullif(field):
    def modifier(self, record, to_attr):
        value = record[field]
        return value and value.strip() or None

    return modifier


class WooCommerceProductAttributeExportMapper(Component):
    _name = "woocommerce.product.attribute.export.mapper"
    _inherit = "woocommerce.export.mapper"

    _apply_on = "woocommerce.product.attribute"

    @mapping
    def name(self, record):
        return {"name": record.name}
