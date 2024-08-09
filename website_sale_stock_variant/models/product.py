# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_inventory_availability = fields.Selection(
        selection=[
            ("never", "Sell regardless of inventory"),
            (
                "always",
                "Show inventory on website " "and prevent sales if not enough stock",
            ),
        ],
        string="Inventory Availability",
        help="Adds an inventory availability status on the web product page.",
        default="never",
        compute="_compute_variant_inventory_availability",
        store=True,
        readonly=False,
    )

    def _compute_variant_inventory_availability(self):
        for rec in self:
            rec.variant_inventory_availability = (
                "always"
                if rec.product_tmpl_id.inventory_availability == "always"
                else "never"
            )
