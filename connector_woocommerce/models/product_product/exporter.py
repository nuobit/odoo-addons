# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
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
        # Descomentar, funciona ok
        self._export_dependency(
            relation.public_categ_ids, "woocommerce.product.public.category"
        )
        if len(relation.product_tmpl_id.product_variant_ids) > 1:
            self._export_dependency(
                relation.product_tmpl_id, "woocommerce.product.template"
            )

        # images_to_export = (relation.image_1920 and relation.product_variant_image_ids)
        # for image in self.env['ir.attachment'].search([('res_model','=','product.product'),('res_id','=',relation.id)]):
        #     attachments_to_export= self.env['ir.attachment'].search([('res_model','=','product.product'),('res_id','=',relation.id)])
        # for image in (relation.image_1920 and relation.product_variant_image_ids) :
        # with self.backend_record.wordpress_backend_id.work_on("wordpress.ir.attachment") as work:
        #     exporter = work.component(usage="record.exporter")
        #     return exporter.run(relation)
        att1 = self.env['ir.attachment'].search(
            [
                ('res_model', '=', relation._name),
                ('res_id', '=', relation.id),
                ('res_field', '=', 'image_variant_1920'),
            ]
        )
        att2 = self.env['ir.attachment'].search(
            [
                ('res_model', '=', relation.product_variant_image_ids._name),
                ('res_id', 'in', relation.product_variant_image_ids.ids),
                ('res_field', '=', 'image_1920'),

            ]
        )
        for attachment in att1 + att2:
            self._export_dependency(
                attachment, "wordpress.ir.attachment",
            )
