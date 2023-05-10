# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductTemplateBatchDirectExporter(Component):
    """Export the WooCommerce Product template.

    For every Product template in the list, execute inmediately.
    """

    _name = "woocommerce.product.template.batch.direct.exporter"
    _inherit = "woocommerce.batch.direct.exporter"

    _apply_on = "woocommerce.product.template"


class WooCommerceProductTemplateBatchDelayedExporter(Component):
    """Export the WooCommerce Product Template.

    For every Product template in the list, a delayed job is created.
    """

    _name = "woocommerce.product.template.batch.delayed.exporter"
    _inherit = "woocommerce.batch.delayed.exporter"

    _apply_on = "woocommerce.product.template"


class WooCommerceProductTemplateExporter(Component):
    _name = "woocommerce.product.template.record.direct.exporter"
    _inherit = "woocommerce.record.direct.exporter"

    _apply_on = "woocommerce.product.template"

    def _export_dependencies(self, relation):
        # TODO: check with values tranlatables
        self._export_dependency(
            relation,
            "woocommerce.product.attribute.value",
        )
        for line in relation.attribute_line_ids:
            for value in line.value_ids:
                self._export_dependency(
                    value,
                    "woocommerce.product.attribute.value",
                )
        att1 = self.env['ir.attachment'].search(
            [
                "&", "&",
                ('res_model', '=', relation._name),
                ('res_id', '=', relation.id),
                ('res_field', '=', 'image_1920'),
            ]
        )
        att2 = self.env['ir.attachment'].search(
            [
                ('res_model', '=', relation.product_template_image_ids._name),
                ('res_id', 'in', relation.product_template_image_ids.ids),
                ('res_field', '=', 'image_1920'),

            ]
        )
        for attachment in att1 + att2:
            self._export_dependency(
                attachment, "wordpress.ir.attachment",
            )
