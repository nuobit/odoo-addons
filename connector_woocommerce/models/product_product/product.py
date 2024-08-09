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
