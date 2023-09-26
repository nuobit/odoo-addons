# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping
from odoo.addons.connector_extension.components.mapper import required


def nullif(field):
    def modifier(self, record, to_attr):
        value = record[field]
        return value and value.strip() or None

    return modifier


class WooCommerceProductAttributeValueExportMapper(Component):
    _name = "woocommerce.product.attribute.value.export.mapper"
    _inherit = "woocommerce.export.mapper"

    _apply_on = "woocommerce.product.attribute.value"

    @required("name")
    @changed_by("name")
    @mapping
    def name(self, record):
        return {
            "name": record.with_context(lang=self.backend_record.language_id.code).name
        }

    @required("parent_id")
    @changed_by("attribute_id")
    @mapping
    def parent_id(self, record):
        binder = self.binder_for("woocommerce.product.attribute")
        values = binder.get_external_dict_ids(record.attribute_id)
        return {"parent_id": values["id"] or None}

    @changed_by("attribute_id")
    @mapping
    def parent_name(self, record):
        return {
            "parent_name": record.attribute_id.with_context(
                lang=self.backend_record.language_id.code
            ).name
        }
