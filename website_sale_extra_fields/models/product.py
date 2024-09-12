# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_public_description = fields.Text(
        translate=True,
    )
    variant_is_published = fields.Boolean(
        compute="_compute_variant_is_published",
        store=True,
        readonly=False,
    )

    # This compute without depends is used to compute the field on install,
    # but it's set and updated on template_is_published with inverse
    def _compute_variant_is_published(self):
        for rec in self:
            rec.variant_is_published = rec.product_tmpl_id.is_published

    product_variant_image_attachment_ids = fields.Many2many(
        comodel_name="attachment.grouped",
        compute="_compute_product_variant_image_attachment_ids",
    )

    def _compute_product_variant_image_attachment_ids(self):
        for rec in self:
            if self.env.context.get("include_main_product_image") == "first":
                rec._create_main_product_variant_image_attachment(is_first=True)
            for variant_image in rec.product_variant_image_ids:
                if variant_image.image_1920:
                    attachment = self.env["ir.attachment"].search(
                        [
                            ("res_model", "=", variant_image._name),
                            ("res_id", "in", variant_image.ids),
                            ("res_field", "=", "image_1920"),
                        ]
                    )
                    rec.product_variant_image_attachment_ids = [
                        (
                            0,
                            0,
                            {
                                "attachment_id": attachment.id,
                                "sequence": variant_image.sequence,
                            },
                        )
                    ]
            if self.env.context.get("include_main_product_image") == "last":
                rec._create_main_product_variant_image_attachment(is_first=False)
            if not rec.product_variant_image_attachment_ids:
                rec.product_variant_image_attachment_ids = self.env[
                    "attachment.grouped"
                ]

    product_document_attachment_ids = fields.Many2many(
        comodel_name="attachment.grouped",
        compute="_compute_product_document_attachment_ids",
    )

    def _compute_product_document_attachment_ids(self):
        for rec in self:
            for doc in rec.document_ids:
                rec.product_document_attachment_ids = [
                    (
                        0,
                        0,
                        {
                            "attachment_id": doc.attachment_id.id,
                            "sequence": doc.sequence,
                        },
                    )
                ]
            if not rec.product_document_attachment_ids:
                rec.product_document_attachment_ids = self.env["attachment.grouped"]

    def _create_main_product_variant_image_attachment(self, is_first=True):
        self.ensure_one()
        attachment = self.env["ir.attachment"].search(
            [
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
                ("res_field", "=", "image_variant_1920"),
            ]
        )
        # TODO: Duplicated code in product_template
        if attachment:
            if is_first:
                sequence = (
                    min(self.product_variant_image_ids.mapped("sequence")) - 1
                    if self.product_variant_image_ids
                    else 1
                )
            else:
                sequence = (
                    max(self.product_variant_image_ids.mapped("sequence")) + 1
                    if self.product_variant_image_ids
                    else 1
                )
            self.product_variant_image_attachment_ids = [
                (
                    0,
                    0,
                    {
                        "attachment_id": attachment.id,
                        "sequence": sequence,
                    },
                )
            ]
