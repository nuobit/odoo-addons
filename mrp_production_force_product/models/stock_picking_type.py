# Copyright 2025 NuoBiT - Bijaya Kumal <bkumal@nuobit.com>
# Copyright 2025 NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    force_product_id = fields.Many2one(
        "product.product", domain="[('type', '=', 'product')]"
    )

    def has_forced_product(self):
        """Check if the picking type has a forced product."""
        self.ensure_one()
        return self.code == "mrp_operation" and self.force_product_id
