# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceWPMLProductProductBatchDirectExporter(Component):
    """Export the WooCommerce WPML Product Product.

    For every Product Product in the list, execute inmediately.
    """

    _name = "woocommerce.wpml.product.product.batch.direct.exporter"
    _inherit = "woocommerce.wpml.batch.direct.exporter"

    _apply_on = "woocommerce.wpml.product.product"


class WooCommerceWPMLProductProductBatchDelayedExporter(Component):
    """Export the WooCommerce WPML Product Product.

    For every Product Product in the list, a delayed job is created.
    """

    _name = "woocommerce.wpml.product.product.batch.delayed.exporter"
    _inherit = "woocommerce.wpml.batch.delayed.exporter"

    _apply_on = "woocommerce.wpml.product.product"


class WooCommerceWPMLProductProductExporter(Component):
    _name = "woocommerce.wpml.product.product.record.direct.exporter"
    _inherit = "woocommerce.wpml.record.direct.exporter"

    _apply_on = "woocommerce.wpml.product.product"

    def _export_dependencies(self, relation):
        # In the case of a woocommerce simple product (Product template with one variant)
        # we need to export the dependencies of the product template because
        # it's the product template that will be exported instead of product product
        if relation.env.context.get("export_wo_acc_p"):
            self._export_dependency(
                relation.with_context(export_wo_acc_p=True).product_tmpl_id,
                "woocommerce.wpml.product.template",
            )
        else:
            self._export_dependency(
                relation.product_tmpl_id,
                "woocommerce.wpml.product.template",
            )
        for line in relation.product_tmpl_id.attribute_line_ids:
            self._export_dependency(
                line.attribute_id,
                "woocommerce.wpml.product.attribute",
            )
            for value in line.value_ids:
                self._export_dependency(
                    value,
                    "woocommerce.wpml.product.attribute.value",
                )
        for attribute_line in relation.attribute_line_ids:
            self._export_dependency(
                attribute_line.attribute_id,
                "woocommerce.wpml.product.attribute",
            )

        # TODO: Adapt wordpress ir checksum to wordpress wpml ir checksum before uncommenting
        # product_image_attachments = relation.with_context(
        #     include_main_product_image=self.backend_record.use_main_product_image
        # ).product_variant_image_attachment_ids
        # if (
        #     product_image_attachments
        #     and len(relation.product_tmpl_id.product_variant_ids) > 1
        # ):
        #     if self.backend_record.wordpress_backend_id:
        #         with self.backend_record.wordpress_backend_id.work_on(
        #             "wordpress.wpml.ir.checksum"
        #         ) as work:
        #             exporter = work.component(self._usage)
        #             exporter._export_dependency(
        #                 product_image_attachments[0].attachment_id.checksum_id,
        #                 "wordpress.wpml.ir.checksum",
        #             )
        # if relation.product_document_attachment_ids:
        #     if self.backend_record.wordpress_backend_id:
        #         with self.backend_record.wordpress_backend_id.work_on(
        #             "wordpress.wpml.ir.checksum"
        #         ) as work:
        #             exporter = work.component(self._usage)
        #             for attachment in relation.product_document_attachment_ids:
        #                 exporter._export_dependency(
        #                     attachment.attachment_id.checksum_id,
        #                     "wordpress.wpml.ir.checksum",
        #                 )
