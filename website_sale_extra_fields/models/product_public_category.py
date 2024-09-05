# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    description = fields.Text(
        translate=True,
    )

    slug_name = fields.Char(
        translate=True,
    )
