# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductTemplateDocument(models.Model):
    _name = "product.template.document"
    _inherit = "product.document"
    _description = "Product Template Document"

    template_id = fields.Many2one(
        comodel_name="product.template",
        string="Product Template",
        required=True,
    )
