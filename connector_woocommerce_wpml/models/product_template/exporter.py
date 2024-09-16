# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceWPMLProductTemplateBatchDirectExporter(Component):
    """Export the WooCommerce WPML Product Template.

    For every Product Public Category in the list, execute inmediately.
    """

    _name = "woocommerce.wpml.product.template.batch.direct.exporter"
    _inherit = "woocommerce.wpml.batch.direct.exporter"

    _apply_on = "woocommerce.wpml.product.template"


class WooCommerceWPMLProductTemplateBatchDelayedExporter(Component):
    """Export the WooCommerce WPML Product Template.

    For every Product Public Category in the list, a delayed job is created.
    """

    _name = "woocommerce.wpml.product.template.batch.delayed.exporter"
    _inherit = "woocommerce.wpml.batch.delayed.exporter"

    _apply_on = "woocommerce.wpml.product.template"


class WooCommerceWPMLProductTemplateExporter(Component):
    _name = "woocommerce.wpml.product.template.record.direct.exporter"
    _inherit = "woocommerce.wpml.record.direct.exporter"

    _apply_on = "woocommerce.wpml.product.template"

    def _export_dependencies(self, relation):
        for category in relation.public_categ_ids:
            self._export_dependency(
                category, "woocommerce.wpml.product.public.category"
            )
        for line in relation.attribute_line_ids:
            self._export_dependency(
                line.attribute_id,
                "woocommerce.wpml.product.attribute",
            )
            for value in line.value_ids:
                self._export_dependency(
                    value,
                    "woocommerce.wpml.product.attribute.value",
                )
        if not relation.env.context.get("export_wo_alt_p"):
            for alternative_product in relation.alternative_product_ids:
                self._export_dependency(
                    alternative_product.with_context(export_wo_alt_p=True),
                    "woocommerce.wpml.product.template",
                )

        if not relation.env.context.get("export_wo_acc_p"):
            for accessory_product in relation.accessory_product_ids:
                if accessory_product.product_tmpl_id.has_attributes:
                    self._export_dependency(
                        accessory_product.with_context(export_wo_acc_p=True),
                        "woocommerce.wpml.product.product",
                    )
                else:
                    self._export_dependency(
                        accessory_product.product_tmpl_id.with_context(
                            export_wo_acc_p=True
                        ),
                        "woocommerce.wpml.product.template",
                    )
        # TODO: Adapt wordpress ir checksum to wordpress wpml ir checksum before uncommenting
        # if self.backend_record.wordpress_backend_id:
        #     with self.backend_record.wordpress_backend_id.work_on(
        #         "wordpress.wpml.ir.checksum"
        #     ) as work:
        #         exporter = work.component(self._usage)
        #         product_image_attachments = relation.with_context(
        #             include_main_product_image=self.backend_record.use_main_product_image
        #         ).product_image_attachment_ids
        #         for image_attachment in product_image_attachments:
        #             exporter._export_dependency(
        #                 image_attachment.attachment_id.checksum_id,
        #                 "wordpress.wpml.ir.checksum",
        #             )
        #         for document_attachment in relation.product_document_attachment_ids:
        #             exporter._export_dependency(
        #                 document_attachment.attachment_id.checksum_id,
        #                 "wordpress.wpml.ir.checksum",
        #             )
