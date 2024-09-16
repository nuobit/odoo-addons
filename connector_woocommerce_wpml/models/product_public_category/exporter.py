# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceWPMLProductPublicCategoryBatchDirectExporter(Component):
    """Export the WooCommerce WPML Product Public Category.

    For every Product Public Category in the list, execute inmediately.
    """

    _name = "woocommerce.wpml.product.public.category.batch.direct.exporter"
    _inherit = "woocommerce.wpml.batch.direct.exporter"

    _apply_on = "woocommerce.wpml.product.public.category"


class WooCommerceWPMLProductPublicCategoryBatchDelayedExporter(Component):
    """Export the WooCommerce WPML Product Public Category.

    For every Product Public Category in the list, a delayed job is created.
    """

    _name = "woocommerce.wpml.product.public.category.batch.delayed.exporter"
    _inherit = "woocommerce.wpml.batch.delayed.exporter"

    _apply_on = "woocommerce.wpml.product.public.category"


class WooCommerceWPMLProductPublicCategoryExporter(Component):
    _name = "woocommerce.wpml.product.public.category.record.direct.exporter"
    _inherit = "woocommerce.wpml.record.direct.exporter"

    _apply_on = "woocommerce.wpml.product.public.category"

    def _export_dependencies(self, relation):
        if relation.parent_id:
            self._export_dependency(
                relation.parent_id, "woocommerce.wpml.product.public.category"
            )
