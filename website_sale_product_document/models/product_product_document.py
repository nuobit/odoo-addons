# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductProductDocument(models.Model):
    _name = "product.product.document"
    _inherit = "product.document"
    _description = "Product Product Document"

    product_id = fields.Many2one(
        comodel_name="product.product",
        required=True,
    )
