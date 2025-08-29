# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    website_name = fields.Char(
        translate=True,
    )
    public_description = fields.Text(
        translate=True,
    )
    public_short_description = fields.Text(
        translate=True,
    )
    slug_name = fields.Char(
        translate=True,
    )
