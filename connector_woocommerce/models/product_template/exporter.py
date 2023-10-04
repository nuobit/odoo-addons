# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductTemplateBatchDirectExporter(Component):
    """Export the WooCommerce Product template.

    For every Product template in the list, execute inmediately.
    """

    _name = "woocommerce.product.template.batch.direct.exporter"
    _inherit = "generic.batch.direct.exporter"

    _apply_on = "woocommerce.product.template"


class WooCommerceProductTemplateBatchDelayedExporter(Component):
    """Export the WooCommerce Product Template.

    For every Product template in the list, a delayed job is created.
    """

    _name = "woocommerce.product.template.batch.delayed.exporter"
    _inherit = "generic.batch.delayed.exporter"

    _apply_on = "woocommerce.product.template"


class WooCommerceProductTemplateExporter(Component):
    _name = "woocommerce.product.template.record.direct.exporter"
    _inherit = "woocommerce.record.direct.exporter"

    _apply_on = "woocommerce.product.template"

    def _export_dependencies(self, relation):
        # for category in relation.public_categ_ids:
        #     self._lock_relation(category)
        # for line in relation.attribute_line_ids:
        #     self._lock_relation(line.attribute_id)
        #     for value in line.value_ids:
        #         self._lock_relation(value)
        # if not relation.env.context.get('export_wo_alt_p'):
        #     for alternative_product in relation.alternative_product_ids:
        #         self._lock_relation(alternative_product)
        # if not relation.env.context.get('export_wo_acc_p'):
        #     for accessory_product in relation.accessory_product_ids:
        #         self._lock_relation(accessory_product)

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
                # self._lock_relation(alternative_product)
                self._export_dependency(
                    alternative_product.with_context(export_wo_alt_p=True),
                    "woocommerce.product.template",
                )

        if not relation.env.context.get("export_wo_acc_p"):
            for accessory_product in relation.accessory_product_ids:
                # self._lock_relation(accessory_product)
                self._export_dependency(
                    accessory_product.with_context(export_wo_acc_p=True),
                    "woocommerce.product.product",
                )

        if self.collection.wordpress_backend_id:
            with self.collection.wordpress_backend_id.work_on(
                "wordpress.ir.attachment"
            ) as work:
                exporter = work.component(self._usage)
                for attachment in relation.product_attachment_ids:
                    exporter._export_dependency(
                        attachment.attachment_id,
                        "wordpress.ir.attachment",
                    )
