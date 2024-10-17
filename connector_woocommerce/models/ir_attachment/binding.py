# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class WordPressIrAttachment(models.Model):
    _inherit = "wordpress.ir.attachment"

    @api.model
    def _get_woocommerce_base_domain(self):
        product_template = (
            self.env["product.template"]
            .with_context(active_test=False)
            .search(
                [
                    ("woocommerce_enabled", "=", True),
                    ("has_attributes", "!=", False),
                ]
            )
        )
        product_variant = (
            self.env["product.product"]
            .with_context(active_test=False)
            .search(
                [
                    ("product_tmpl_id.woocommerce_enabled", "=", True),
                    ("product_tmpl_id.has_attributes", "=", True),
                ]
            )
        )
        attachments = (
            product_template.product_image_attachment_ids.attachment_id
            + product_template.product_document_attachment_ids.attachment_id
            + product_variant.product_variant_image_attachment_ids.attachment_id
            + product_variant.product_document_attachment_ids.attachment_id
        )
        return [("id", "in", attachments.ids)]

    def export_product_attachment_since(self, backend_record=None, since_date=None):
        domain = self._get_woocommerce_base_domain()
        if since_date:
            domain += [
                (
                    "write_date",
                    ">",
                    since_date.strftime("%Y-%m-%dT%H:%M:%S"),
                )
            ]
        self.export_batch(backend_record.wordpress_backend_id, domain=domain)
        return True
