# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductProductBatchDirectExporter(Component):
    """Export the WooCommerce Product product.

    For every Product product in the list, execute inmediately.
    """

    _name = "woocommerce.product.product.batch.direct.exporter"
    _inherit = "woocommerce.batch.direct.exporter"

    _apply_on = "woocommerce.product.product"


class WooCommerceProductProductBatchDelayedExporter(Component):
    """Export the WooCommerce Product Product.

    For every Product product in the list, a delayed job is created.
    """

    _name = "woocommerce.product.product.batch.delayed.exporter"
    _inherit = "woocommerce.batch.delayed.exporter"

    _apply_on = "woocommerce.product.product"


class WooCommerceProductProductExporter(Component):
    _name = "woocommerce.product.product.record.direct.exporter"
    _inherit = "woocommerce.record.direct.exporter"

    _apply_on = "woocommerce.product.product"

    def _export_dependencies(self, relation):
        self._export_dependency(
            relation.product_tmpl_id,
            "woocommerce.product.template",
        )
        for line in relation.attribute_line_ids:
            self._export_dependency(
                line.attribute_id,
                "woocommerce.product.attribute",
            )
        if len(relation.product_tmpl_id.product_variant_ids) > 1:
            attachment = self.env["ir.attachment"].search(
                [
                    ("res_model", "=", relation._name),
                    ("res_id", "=", relation.id),
                    ("res_field", "=", "image_variant_1920"),
                ]
            )
            if self.collection.wordpress_backend_id:
                with self.collection.wordpress_backend_id.work_on(
                    "wordpress.ir.attachment"
                ) as work:
                    exporter = work.component(self._usage)
                    exporter._export_dependency(
                        attachment,
                        "wordpress.ir.attachment",
                    )

    # This _has_to_skip allow to export the product dependencies,
    # including the product template, when the product
    # created in woocommerce is a simple product
    def _has_to_skip(self, binding, relation):
        res = super()._has_to_skip(binding, relation)
        if len(relation.product_tmpl_id.product_variant_ids) <= 1:
            self._export_dependencies(relation.product_variant_id)
            res = True
        return res
