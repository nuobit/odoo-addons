# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_published = fields.Boolean(
        string="Product published",
        compute="_compute_template_is_published",
        inverse="_inverse_template_is_published",
        store=True,
        readonly=False,
    )
    button_is_published = fields.Boolean(
        string="Button product published",
        related="is_published",
    )

    @api.depends("product_variant_ids.variant_is_published")
    def _compute_template_is_published(self):
        for rec in self:
            published_variants = rec._origin.product_variant_ids.filtered(
                lambda x: x.variant_is_published
            )
            rec.is_published = bool(published_variants)

    def _inverse_template_is_published(self):
        for rec in self:
            rec.product_variant_ids.variant_is_published = rec.is_published
