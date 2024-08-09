# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    inventory_availability = fields.Selection(
        compute="_compute_inventory_availability",
        inverse="_inverse_inventory_availability",
        store=True,
        readonly=False,
    )

    @api.depends("product_variant_ids.variant_inventory_availability")
    def _compute_inventory_availability(self):
        for rec in self:
            never_variants_availability = rec.product_variant_ids.filtered(
                lambda x: x.variant_inventory_availability == "never"
            )
            if never_variants_availability:
                rec.inventory_availability = "never"
            else:
                rec.inventory_availability = "always"

    def _inverse_inventory_availability(self):
        for rec in self:
            if rec.inventory_availability in ("always", "never"):
                rec.product_variant_ids.variant_inventory_availability = (
                    rec.inventory_availability
                )
