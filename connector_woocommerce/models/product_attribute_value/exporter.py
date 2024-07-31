# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductAttributeValueBatchDirectExporter(Component):
    """Export the WooCommerce Product Attibute Value.

    For every Product Attibute Value in the list, execute inmediately.
    """

    _name = "woocommerce.product.attribute.value.batch.direct.exporter"
    _inherit = "connector.extension.generic.batch.direct.exporter"

    _apply_on = "woocommerce.product.attribute.value"


class WooCommerceProductAttributeValueBatchDelayedExporter(Component):
    """Export the WooCommerce Product Attibute Value.

    For every Product Attibute Value in the list, a delayed job is created.
    """

    _name = "woocommerce.product.attribute.value.batch.delayed.exporter"
    _inherit = "connector.extension.generic.batch.delayed.exporter"

    _apply_on = "woocommerce.product.attribute.value"


class WooCommerceProductAttributeValueExporter(Component):
    _name = "woocommerce.product.attribute.value.record.direct.exporter"
    _inherit = "woocommerce.record.direct.exporter"

    _apply_on = "woocommerce.product.attribute.value"

    def _export_dependencies(self, relation):
        self._export_dependency(
            relation.attribute_id,
            "woocommerce.product.attribute",
        )
