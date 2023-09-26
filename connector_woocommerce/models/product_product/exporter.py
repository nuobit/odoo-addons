# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductProductBatchDirectExporter(Component):
    """Export the WooCommerce Product product.

    For every Product product in the list, execute inmediately.
    """

    _name = "woocommerce.product.product.batch.direct.exporter"
    _inherit = "generic.batch.direct.exporter"

    _apply_on = "woocommerce.product.product"


class WooCommerceProductProductBatchDelayedExporter(Component):
    """Export the WooCommerce Product Product.

    For every Product product in the list, a delayed job is created.
    """

    _name = "woocommerce.product.product.batch.delayed.exporter"
    _inherit = "generic.batch.delayed.exporter"

    _apply_on = "woocommerce.product.product"


class WooCommerceProductProductExporter(Component):
    _name = "woocommerce.product.product.record.direct.exporter"
    _inherit = "woocommerce.record.direct.exporter"

    _apply_on = "woocommerce.product.product"

    def _export_dependencies(self, relation):
        # In the case of a woocommerce simple product (Product template with one variant)
        # we need to export the dependencies of the product template because
        # it's the product template that will be exported instead of product product
        self._export_dependency(
            relation.product_tmpl_id,
            "woocommerce.product.template",
        )
        for attribute_line in relation.attribute_line_ids:
            self._export_dependency(
                attribute_line.attribute_id,
                "woocommerce.product.attribute",
            )
        if (
            relation.product_attachment_ids
            and len(relation.product_tmpl_id.product_variant_ids) > 1
        ):
            if self.collection.wordpress_backend_id:
                with self.collection.wordpress_backend_id.work_on(
                    "wordpress.ir.attachment"
                ) as work:
                    exporter = work.component(self._usage)
                    exporter._export_dependency(
                        relation.product_attachment_ids[0].attachment_id,
                        "wordpress.ir.attachment",
                    )
