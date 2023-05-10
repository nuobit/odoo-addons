# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.product.template",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
    )
