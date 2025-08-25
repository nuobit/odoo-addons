# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductTemplateBatchDirectExporter(Component):
    """Export the WooCommerce Product template.

    For every Product template in the list, execute inmediately.
    """

    _name = "woocommerce.product.template.batch.direct.exporter"
    _inherit = "connector.extension.generic.batch.direct.exporter"

    _apply_on = "woocommerce.product.template"


class WooCommerceProductTemplateBatchDelayedExporter(Component):
    """Export the WooCommerce Product Template.

    For every Product template in the list, a delayed job is created.
    """

    _name = "woocommerce.product.template.batch.delayed.exporter"
    _inherit = "connector.extension.generic.batch.delayed.exporter"

    _apply_on = "woocommerce.product.template"


class WooCommerceProductTemplateExporter(Component):
    _name = "woocommerce.product.template.record.direct.exporter"
    _inherit = "woocommerce.record.direct.exporter"

    _apply_on = "woocommerce.product.template"

    def _export_dependencies(self, relation):
        for category in relation.public_categ_ids:
            self._export_dependency(category, "woocommerce.product.public.category")
        for line in relation.attribute_line_ids:
            self._export_dependency(
                line.attribute_id,
                "woocommerce.product.attribute",
            )
            for value in line.value_ids:
                self._export_dependency(
                    value,
                    "woocommerce.product.attribute.value",
                )
        if not relation.env.context.get("export_wo_alt_p"):
            for alternative_product in relation.alternative_product_ids:
                self._export_dependency(
                    alternative_product.with_context(export_wo_alt_p=True),
                    "woocommerce.product.template",
                )

        # TODO: Review circular reference. If at the same time one product variant
        #  is an accessory product of the product template, probably we will have
        #  a circular reference.
        if not relation.env.context.get("export_wo_acc_p"):
            for accessory_product in relation.accessory_product_ids:
                if accessory_product.product_tmpl_id.has_attributes:
                    self._export_dependency(
                        accessory_product.with_context(export_wo_acc_p=True),
                        "woocommerce.product.product",
                    )
                else:
                    self._export_dependency(
                        accessory_product.product_tmpl_id.with_context(
                            export_wo_acc_p=True
                        ),
                        "woocommerce.product.template",
                    )

        if self.backend_record.wordpress_backend_id:
            with self.backend_record.wordpress_backend_id.work_on(
                "wordpress.ir.attachment"
            ) as work:
                exporter = work.component(self._usage)
                product_image_attachments = relation.with_context(
                    include_main_product_image=self.backend_record.use_main_product_image
                ).product_image_attachment_ids
                for image_attachment in product_image_attachments:
                    exporter._export_dependency(
                        image_attachment.attachment_id,
                        "wordpress.ir.attachment",
                    )
                for document_attachment in relation.product_document_attachment_ids:
                    exporter._export_dependency(
                        document_attachment.attachment_id,
                        "wordpress.ir.attachment",
                    )
