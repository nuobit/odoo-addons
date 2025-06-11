# Copyright 2025 NuoBiT - Bijaya Kumal <bkumal@nuobit.com>
# Copyright 2025 NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    has_forced_product = fields.Boolean(compute="_compute_has_forced_product")

    @api.depends("picking_type_id")
    def _compute_has_forced_product(self):
        for record in self:
            record.has_forced_product = record.picking_type_id.has_forced_product()

    @api.depends("bom_id", "picking_type_id")
    def _compute_product_id(self):
        super()._compute_product_id()
        for production in self:
            pt = production.picking_type_id
            if pt.has_forced_product():
                production.product_id = pt.force_product_id
        return

    @api.constrains("product_id", "picking_type_id", "product_qty")
    def _check_force_product(self):
        for record in self:
            if record.picking_type_id.has_forced_product():
                if record.product_id != record.picking_type_id.force_product_id:
                    raise ValidationError(_("Product must match forced product."))
