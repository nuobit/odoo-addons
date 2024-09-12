# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models

from odoo.addons.http_routing.models.ir_http import slugify


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    description = fields.Text(
        translate=True,
    )
    slug_name = fields.Char(
        translate=True,
        required=True,
        compute="_compute_slug_name",
        store=True,
        readonly=False,
    )

    @api.depends("name")
    def _compute_slug_name(self):
        for rec in self:
            if not rec.slug_name:
                rec.slug_name = slugify(rec.name)
