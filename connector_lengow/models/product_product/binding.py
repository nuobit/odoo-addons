# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    lengow_bind_ids = fields.One2many(
        comodel_name="lengow.product.product",
        inverse_name="odoo_id",
        string="Lengow Bindings",
    )


class ProductProductBinding(models.Model):
    _name = "lengow.product.product"
    _inherit = "lengow.binding"
    _inherits = {"product.product": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
        ondelete="cascade",
    )
    lengow_sku = fields.Char(string="SKU")

    _sql_constraints = [
        (
            "lengow_product_external_uniq",
            "unique(backend_id, lengow_sku)",
            "A binding already exists with the same External (Lengow) ID.",
        ),
    ]
