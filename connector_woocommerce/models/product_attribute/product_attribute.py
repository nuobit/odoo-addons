# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.product.attribute",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        context={"active_test": False},
    )