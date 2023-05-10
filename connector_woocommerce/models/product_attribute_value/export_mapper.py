# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


def nullif(field):
    def modifier(self, record, to_attr):
        value = record[field]
        return value and value.strip() or None

    return modifier


class WooCommerceProductAttributeValueExportMapper(Component):
    _name = "woocommerce.product.attribute.value.export.mapper"
    _inherit = "woocommerce.export.mapper"

    _apply_on = "woocommerce.product.attribute.value"

    direct = [
        ("name", "name"),
    ]

    # @mapping
    # def name(self, record):
    #     return {"name": record.name}

    @mapping
    def parent_id(self, record):
        parent = record.attribute_id
        external_id = self.binder_for("woocommerce.product.attribute").to_external(
            parent, wrap=False
        )
        self.check_external_id(external_id, parent)
        return {"parent_id": external_id}
