# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models
from odoo.osv import expression


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
        # The files the attachment fields of these products collect, found
        # through their owner records: a domain on ir.attachment cannot follow
        # res_id, and reading those computed fields creates records.
        images = self.env["product.image"].search(
            [
                "|",
                ("product_tmpl_id", "in", product_template.ids),
                ("product_variant_id", "in", product_variant.ids),
            ]
        )
        template_documents = self.env["product.template.document"].search(
            [("template_id", "in", product_template.ids)]
        )
        variant_documents = self.env["product.product.document"].search(
            [("product_id", "in", product_variant.ids)]
        )
        return expression.OR(
            [
                [
                    ("res_model", "=", images._name),
                    ("res_field", "=", "image_1920"),
                    ("res_id", "in", images.ids),
                ],
                [
                    ("res_model", "=", template_documents._name),
                    ("res_field", "=", "datas"),
                    ("res_id", "in", template_documents.ids),
                ],
                [
                    ("res_model", "=", variant_documents._name),
                    ("res_field", "=", "datas"),
                    ("res_id", "in", variant_documents.ids),
                ],
            ]
        )

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
        self.with_delay().export_batch(
            backend_record.wordpress_backend_id, domain=domain
        )
        return True
