# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.product.template",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
    )
    woocommerce_write_date = fields.Datetime(
        compute="_compute_woocommerce_write_date",
        store=True,
    )
    # woocommerce_upsell_write_date = fields.Datetime(
    #     compute="_compute_woocommerce_write_date",
    #     store=True,
    # )

    @api.depends(
        "is_published",
        "name",
        "lst_price",
        "active",
        "product_variant_id.qty_available",
        "image_1920",
        "default_code",
        "qty_available",
        "description",
        "public_categ_ids",
        "attribute_line_ids",
        "public_description",
    )
    def _compute_woocommerce_write_date(self):
        for rec in self:
            if rec.is_published or rec.woocommerce_write_date:
                rec.woocommerce_write_date = fields.Datetime.now()

    public_description = fields.Text(
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

    product_attachment_ids = fields.Many2many(
        comodel_name="product.attachment",
        compute="_compute_product_attachment_ids",
    )

    def _compute_product_attachment_ids(self):
        for rec in self:
            attachment = self.env["ir.attachment"].search(
                [
                    ("res_model", "=", rec._name),
                    ("res_id", "=", rec.id),
                    ("res_field", "=", "image_1920"),
                ]
            )
            if attachment:
                rec.product_attachment_ids = [
                    (
                        0,
                        0,
                        {
                            "attachment_id": attachment.id,
                            "sequence": min(
                                rec.product_template_image_ids.mapped("sequence")
                            )
                            - 1
                            if rec.product_template_image_ids
                            else 1,
                        },
                    )
                ]
            for template_image in rec.product_template_image_ids:
                if template_image.image_1920:
                    attachment = self.env["ir.attachment"].search(
                        [
                            ("res_model", "=", template_image._name),
                            ("res_id", "=", template_image.id),
                            ("res_field", "=", "image_1920"),
                        ]
                    )
                    rec.product_attachment_ids = [
                        (
                            0,
                            0,
                            {
                                "attachment_id": attachment.id,
                                "sequence": template_image.sequence,
                            },
                        )
                    ]
            if not rec.product_attachment_ids:
                rec.product_attachment_ids = self.env["product.attachment"]
