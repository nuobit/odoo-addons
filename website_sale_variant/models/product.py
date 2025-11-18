# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_is_published = fields.Boolean(
        string="Variant published",
        help="Indicates if this specific variant is published on the website",
        compute="_compute_variant_is_published",
        store=True,
        readonly=False,
    )

    # This compute without depends is used to compute the field on install,
    # but it's set and updated on template_is_published with inverse
    def _compute_variant_is_published(self):
        for rec in self:
            rec.variant_is_published = rec.product_tmpl_id.is_published
