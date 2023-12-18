# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductProductBinding(models.Model):
    _name = "sapb1.product.product"
    _inherit = "sapb1.binding"
    _inherits = {"product.product": "odoo_id"}
    _description = "SAP B1 Product Binding"

    odoo_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
        ondelete="cascade",
    )

    sapb1_sku = fields.Char(
        string="SKU",
        required=True,
    )

    _sql_constraints = [
        (
            "sapb1_product_external_uniq",
            "unique(backend_id, sapb1_sku)",
            "A binding already exists with the same External (SAP B1) ID.",
        ),
    ]
