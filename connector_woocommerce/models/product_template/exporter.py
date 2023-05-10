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
        # for alternative_product in relation.alternative_product_ids:
        #     rel_id = relation.id
        #     ap = self.model._context.get("alternative_product")
        #     alternative_product_list=[]
        #     if ap:
        #         if rel_id not in ap:
        #             alternative_product_list= ap.append(rel_id)
        #         else:
        #             self.model.with_context(export_wo_ap=True)
        #             self._export_dependency(
        #                 alternative_product,
        #                 "woocommerce.product.template",
        #             )
        #     else:
        #         alternative_product_list = [rel_id]
        #     self.model.with_context(alternative_product=alternative_product_list)
        #     # context = self.model._context.copy()
        #     # context["aaa"] = [1,2,3]
        #     # self.model._context = context
        #     self._export_dependency(
        #         alternative_product,
        #         "woocommerce.product.template",
        #     )

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
        #
        # if self._context.get("alternative_product"):
        #     if relation.id not in self._context["alternative_product"]:
        #         new_context = dict(self._context)
        #         new_context["alternative_product"].append(relation.id)
        #         self.with_context(new_context).export_record(relation)
        #
        # for alternative_product in relation.alternative_product_ids:
        #     if self.model._context.get("alternative_products"):
        #         if relation.id in self._context["alternative_products"]:
        #             return
        #     if self.model._context.get("alternative_products"):
        #         if alternative_product.id not in self.with_context(
        #             "alternative_product"
        #         ):
        #             new_context = dict(self._context)
        #             new_context["alternative_product"].append(alternative_product.id)
        #             self.with_context(
        #                 alternative_products=new_context
        #             )._export_dependency(
        #                 alternative_product, "woocommerce.product.template"
        #             )
        #             # self.with_context(export_ap=True).\
        #             # _export_dependency(alternative_product, "woocommerce.product.template")
        #         else:
        #             self.with_context(export_wo_ap=True)._export_dependency(
        #                 alternative_product, "woocommerce.product.template"
        #             )
