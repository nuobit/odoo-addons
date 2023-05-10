# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.product.public.category",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
    )
