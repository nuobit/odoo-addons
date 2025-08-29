# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.product.product",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        context={"active_test": False},
    )
    woocommerce_write_date = fields.Datetime(
        compute="_compute_woocommerce_write_date",
        store=True,
    )

    @api.depends(
        "is_published",
        "lst_price",
        "type",
        "default_code",
        "image_1920",
        "default_code",
        "qty_available",
        "product_template_attribute_value_ids",
        "variant_public_description",
        "alternative_product_ids",
        "accessory_product_ids",
        "variant_inventory_availability",
        "document_ids",
        "product_tmpl_id",
        "product_tmpl_id.has_attributes",
        "product_tmpl_id.woocommerce_enabled",
    )
    def _compute_woocommerce_write_date(self):
        for rec in self:
            if (
                rec.product_tmpl_id.woocommerce_enabled
                or rec.variant_is_published
                or rec.woocommerce_write_date
            ):
                rec.woocommerce_write_date = fields.Datetime.now()

    # Auxiliar fields for images and documents
    product_variant_image_attachment_ids = fields.Many2many(
        comodel_name="connector.woocommerce.product.attachment",
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
                    "connector.woocommerce.product.attachment"
                ]

    product_document_attachment_ids = fields.Many2many(
        comodel_name="connector.woocommerce.product.attachment",
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
                rec.product_document_attachment_ids = self.env[
                    "connector.woocommerce.product.attachment"
                ]

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
