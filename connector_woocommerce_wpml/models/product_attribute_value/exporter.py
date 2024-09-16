# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceWPMLProductAttributeValueBatchDirectExporter(Component):
    """Export the WooCommerce WPML Product Attibute Value.

    For every Product Attibute Value in the list, execute inmediately.
    """

    _name = "woocommerce.wpml.product.attribute.value.batch.direct.exporter"
    _inherit = "woocommerce.wpml.batch.direct.exporter"

    _apply_on = "woocommerce.wpml.product.attribute.value"


class WooCommerceWPMLProductAttributeValueBatchDelayedExporter(Component):
    """Export the WooCommerce WPML Product Attibute Value.

    For every Product Attibute Value in the list, a delayed job is created.
    """

    _name = "woocommerce.wpml.product.attribute.value.batch.delayed.exporter"
    _inherit = "woocommerce.wpml.batch.delayed.exporter"

    _apply_on = "woocommerce.wpml.product.attribute.value"


class WooCommerceWPMLProductAttributeValueExporter(Component):
    _name = "woocommerce.wpml.product.attribute.value.record.direct.exporter"
    _inherit = "woocommerce.wpml.record.direct.exporter"

    _apply_on = "woocommerce.wpml.product.attribute.value"

    # TODO: When we export attribute values, we need to export the attribute,
    #  the problem is that we need to export attribute first, but we have a problem because
    #  we try to rebind attribute value before export in attribute, so we can't
    #  do search_read.
    def _export_dependencies(self, relation):
        self._export_dependency(
            relation.attribute_id,
            "woocommerce.wpml.product.attribute",
        )
