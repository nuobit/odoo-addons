# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    wordpress_bind_ids = fields.One2many(
        comodel_name="wordpress.product.product",
        inverse_name="odoo_id",
        string="WordPress Bindings",
    )
