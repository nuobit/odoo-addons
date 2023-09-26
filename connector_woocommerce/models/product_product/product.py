# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.product.product",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
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
        "product_tmpl_id",
        "default_code",
        "qty_available",
        "product_template_attribute_value_ids",
        "variant_public_description",
    )
    def _compute_woocommerce_write_date(self):
        for rec in self:
            if rec.is_published or rec.woocommerce_write_date:
                rec.woocommerce_write_date = fields.Datetime.now()

    variant_public_description = fields.Text(
        translate=True,
    )
    variant_is_published = fields.Boolean(
        default=False,
        store=True,
        readonly=False,
    )
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
                    ("res_field", "=", "image_variant_1920"),
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
                                rec.product_variant_image_ids.mapped("sequence")
                            )
                            - 1
                            if rec.product_variant_image_ids
                            else 1,
                        },
                    )
                ]
            for variant_image in rec.product_variant_image_ids:
                if variant_image.image_1920:
                    attachment = self.env["ir.attachment"].search(
                        [
                            ("res_model", "=", variant_image._name),
                            ("res_id", "in", variant_image.ids),
                            ("res_field", "=", "image_1920"),
                        ]
                    )
                    rec.product_attachment_ids = [
                        (
                            0,
                            0,
                            {
                                "attachment_id": attachment.id,
                                "sequence": variant_image.sequence,
                            },
                        )
                    ]
            if not rec.product_attachment_ids:
                rec.product_attachment_ids = self.env["product.attachment"]
