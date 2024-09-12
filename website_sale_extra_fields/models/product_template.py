# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    website_name = fields.Char(
        translate=True,
    )
    public_description = fields.Text(
        translate=True,
    )
    public_short_description = fields.Text(
        translate=True,
    )
    slug_name = fields.Char(
        translate=True,
    )
    is_published = fields.Boolean(
        compute="_compute_template_is_published",
        inverse="_inverse_template_is_published",
        store=True,
        readonly=False,
    )
    button_is_published = fields.Boolean(
        related="is_published",
    )

    @api.depends("product_variant_ids.variant_is_published")
    def _compute_template_is_published(self):
        for rec in self:
            published_variants = rec._origin.product_variant_ids.filtered(
                lambda x: x.variant_is_published
            )
            rec.is_published = bool(published_variants)

    def _inverse_template_is_published(self):
        for rec in self:
            rec.product_variant_ids.variant_is_published = rec.is_published

    product_image_attachment_ids = fields.Many2many(
        comodel_name="attachment.grouped",
        compute="_compute_product_image_attachment_ids",
    )

    def _create_main_product_image_attachment(self, is_first=True):
        self.ensure_one()
        attachment = self.env["ir.attachment"].search(
            [
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
                ("res_field", "=", "image_1920"),
            ]
        )
        if attachment:
            if is_first:
                sequence = (
                    min(self.product_template_image_ids.mapped("sequence")) - 1
                    if self.product_template_image_ids
                    else 1
                )
            else:
                sequence = (
                    max(self.product_template_image_ids.mapped("sequence")) + 1
                    if self.product_template_image_ids
                    else 1
                )
            self.product_image_attachment_ids = [
                (
                    0,
                    0,
                    {
                        "attachment_id": attachment.id,
                        "sequence": sequence,
                    },
                )
            ]

    def _compute_product_image_attachment_ids(self):
        for rec in self:
            if self.env.context.get("include_main_product_image") == "first":
                rec._create_main_product_image_attachment(is_first=True)
            for template_image in rec.product_template_image_ids:
                if template_image.image_1920:
                    attachment = self.env["ir.attachment"].search(
                        [
                            ("res_model", "=", template_image._name),
                            ("res_id", "=", template_image.id),
                            ("res_field", "=", "image_1920"),
                        ]
                    )
                    rec.product_image_attachment_ids = [
                        (
                            0,
                            0,
                            {
                                "attachment_id": attachment.id,
                                "sequence": template_image.sequence,
                            },
                        )
                    ]
            if self.env.context.get("include_main_product_image") == "last":
                rec._create_main_product_image_attachment(is_first=False)
            if not rec.product_image_attachment_ids:
                rec.product_image_attachment_ids = self.env["attachment.grouped"]

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
