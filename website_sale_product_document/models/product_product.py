# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    document_ids = fields.One2many(
        comodel_name="product.product.document",
        inverse_name="product_id",
        string="Documents",
    )
