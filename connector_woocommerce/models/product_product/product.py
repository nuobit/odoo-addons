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
        "is_published", "lst_price", "default_code", "image_1920", "product_tmpl_id"
    )
    def _compute_woocommerce_write_date(self):
        for rec in self:
            if rec.is_published or rec.woocommerce_write_date:
                rec.woocommerce_write_date = fields.Datetime.now()
