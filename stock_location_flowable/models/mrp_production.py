# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    picking_id = fields.Many2one(comodel_name="stock.picking")
    production_blocked = fields.Boolean(compute="_compute_production_blocked")

    def _compute_production_blocked(self):
        for rec in self:
            rec.production_blocked = bool(
                self.env["stock.location"].search_count(
                    [("flowable_production_id", "=", rec.id)]
                )
            )

    @api.constrains("product_id", "move_raw_ids", "location_dest_id")
    def _check_production_lines(self):
        for rec in self:
            if not rec.picking_type_id.flowable_operation:
                super(MrpProduction, rec)._check_production_lines()

    @api.constrains("state")
    def _check_flowable_blocked(self):
        for rec in self:
            if rec.state == "cancel" and rec.picking_id:
                raise ValidationError(
                    _(
                        "You cannot cancel a production with a picking associated."
                        " The mixing is in progress."
                    )
                )

    def write(self, vals):
        for rec in self:
            if (
                rec.picking_id
                and rec.picking_type_id.flowable_operation
                and rec.state == "to_close"
            ):
                raise ValidationError(
                    _(
                        "You cannot modify a mix production with a picking associated."
                        " The mixing is in progress."
                    )
                )
        return super().write(vals)
