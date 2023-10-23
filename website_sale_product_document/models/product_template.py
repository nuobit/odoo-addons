# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    document_ids = fields.One2many(
        comodel_name="product.template.document",
        inverse_name="template_id",
        string="Documents",
    )
