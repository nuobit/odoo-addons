# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductPublicCategoryBatchDirectExporter(Component):
    """Export the WooCommerce Product Public Category.

    For every Product Public Category in the list, execute inmediately.
    """

    _name = "woocommerce.product.public.category.batch.direct.exporter"
    _inherit = "generic.batch.direct.exporter"

    _apply_on = "woocommerce.product.public.category"


class WooCommerceProductPublicCategoryBatchDelayedExporter(Component):
    """Export the WooCommerce Product Public Category.

    For every Product Public Category in the list, a delayed job is created.
    """

    _name = "woocommerce.product.public.category.batch.delayed.exporter"
    _inherit = "generic.batch.delayed.exporter"

    _apply_on = "woocommerce.product.public.category"


class WooCommerceProductPublicCategoryExporter(Component):
    _name = "woocommerce.product.public.category.record.direct.exporter"
    _inherit = "woocommerce.record.direct.exporter"

    _apply_on = "woocommerce.product.public.category"

    def _export_dependencies(self, relation):
        if relation.parent_id:
            self._export_dependency(
                relation.parent_id, "woocommerce.product.public.category"
            )
