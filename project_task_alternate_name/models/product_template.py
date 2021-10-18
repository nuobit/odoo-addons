# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    service_description_type = fields.Selection(
        selection=[
            ("0_brand", "Brand"),
            ("1_type", "Type"),
            ("2_color", "Color"),
            ("3_size", "Size"),
        ]
    )
    is_service_description = fields.Boolean(related="categ_id.is_service_description")
