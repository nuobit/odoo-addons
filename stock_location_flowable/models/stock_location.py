# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import json


class Location(models.Model):
    _inherit = "stock.location"

    flowable_storage = fields.Boolean()
    flowable_blocked = fields.Boolean(compute="_compute_flowable_blocked")
    flowable_blocked_popover = fields.Char(
        string="JSON data for the popover widget",
        compute="_compute_flowable_blocked_popover",
    )
    flowable_capacity = fields.Float(string="Capacity")
    flowable_uom_id = fields.Many2one(string="Unit of Measure", comodel_name="uom.uom")
    flowable_sequence_id = fields.Many2one(
        string="Sequence", comodel_name="ir.sequence", check_company=True
    )
    flowable_allowed_product_ids = fields.Many2many(
        string="Allowed Products", comodel_name="product.product"
    )
    flowable_production_id = fields.Many2one(
        comodel_name="mrp.production",
    )
    flowable_capacity_occupied = fields.Float(
        compute="_compute_flowable_capacity_occupied", store=True
    )
    flowable_percentage_occupied = fields.Float(
        compute="_compute_flowable_percentage_occupied"
    )
    flowable_create_lots = fields.Boolean()

    def _compute_flowable_blocked_popover(self):
        for rec in self:
            rec.flowable_blocked_popover = json.dumps(
                {
                    "title": _("Flowable Location Warning"),
                    "msg": _(
                        "This location is blocked because it has "
                        "a manufacturing order assigned."
                    ),
                }
            )

    @api.depends("flowable_production_id")
    def _compute_flowable_blocked(self):
        for rec in self:
            rec.flowable_blocked = bool(
                rec.flowable_storage and rec.flowable_production_id
            )

    @api.depends("quant_ids.quantity")
    def _compute_flowable_capacity_occupied(self):
        for rec in self:
            if rec.flowable_storage:
                rec.flowable_capacity_occupied = sum(rec.quant_ids.mapped("quantity"))

    @api.depends("flowable_capacity_occupied")
    def _compute_flowable_percentage_occupied(self):
        for rec in self:
            if rec.flowable_capacity <= 0:
                rec.flowable_percentage_occupied = 0
            else:
                rec.flowable_percentage_occupied = (
                    rec.flowable_capacity_occupied / rec.flowable_capacity * 100
                )

    def action_view_mrp_production(self):
        self.ensure_one()
        return {
            "name": _("Manufacturing Orders"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mrp.production",
            "res_id": self.flowable_production_id.id,
        }

    @api.constrains("flowable_uom_id")
    def _check_flowable_uom_id(self):
        for rec in self:
            if rec.flowable_storage:
                if rec.quant_ids.filtered(
                    lambda x: x.product_uom_id != rec.flowable_uom_id and x.quantity > 0
                ):
                    raise ValidationError(
                        _("You have stock movements with different unit of measure")
                    )

    @api.constrains("flowable_capacity_occupied")
    def _check_flowable_capacity_occupied(self):
        for rec in self:
            if rec.usage != "view" and rec.flowable_storage:
                if rec.flowable_capacity_occupied >= rec.flowable_capacity:
                    raise ValidationError(_("Location capacity is full"))

    @api.constrains("flowable_storage")
    def _check_production_linked_flowable_location(self):
        for rec in self:
            if not rec.flowable_storage and rec.flowable_production_id:
                raise ValidationError(
                    _("You cannot disable flowable storage from a blocked location.")
                )

    @api.constrains(
        "flowable_storage",
        "flowable_uom_id",
        "flowable_allowed_product_ids",
        "flowable_capacity",
        "flowable_create_lots",
        "flowable_sequence_id",
    )
    def _check_required_fields_flowable_storage(self):
        for rec in self:
            if rec.usage != "view" and rec.flowable_storage:
                if rec.flowable_capacity <= 0:
                    raise ValidationError(_("Capacity must be greater than 0"))
                if rec.flowable_capacity < rec.flowable_capacity_occupied:
                    raise ValidationError(
                        _("Capacity must be greater than capacity occupied %s")
                        % rec.flowable_capacity_occupied
                    )
                if not rec.flowable_uom_id:
                    raise ValidationError(_("You must select a unit of measure"))
                if not rec.flowable_allowed_product_ids:
                    raise ValidationError(_("You must select products"))
                if rec.flowable_create_lots and not rec.flowable_sequence_id:
                    raise ValidationError(_("You must select a sequence"))

    @api.constrains("flowable_allowed_product_ids", "flowable_uom_id")
    def _check_sequence_products_flowable_capacity(self):
        for rec in self:
            if rec.usage != "view" and rec.flowable_storage:
                if rec.flowable_allowed_product_ids.filtered(
                    lambda x: x.tracking != "lot"
                ):
                    raise ValidationError(
                        _("All allowed products must be tracked by lot")
                    )
                for product in rec.flowable_allowed_product_ids:
                    if product.uom_id != rec.flowable_uom_id:
                        raise ValidationError(
                            _(
                                "The product %s is measured in %s. You can only assign"
                                " products that have the allowed unit of measure"
                            )
                            % (product.name, product.uom_id.name)
                        )

    @api.depends("name", "location_id.complete_name", "usage", "flowable_blocked")
    def _compute_complete_name(self):
        for rec in self:
            if rec.flowable_storage and rec.flowable_blocked:
                rec.complete_name = "%s/%s [%s]" % (
                    rec.location_id.complete_name,
                    rec.name,
                    _("Blocked"),
                )
            else:
                super(Location, rec)._compute_complete_name()

    def name_get(self):
        res = []
        for rec in self:
            name_l = [rec.name]
            if rec.flowable_storage and rec.flowable_blocked:
                name_l.append("[Blocked]")
            res.append((rec.id, " ".join(name_l)))
        return res

    def write(self, vals):
        for rec in self:
            old_allowed_products = self.env["product.product"]
            if "flowable_allowed_product_ids" in vals and vals.get(
                "flowable_storage", rec.flowable_storage
            ):
                old_allowed_products = rec.flowable_allowed_product_ids
            if vals.get("flowable_storage"):
                for product in rec.quant_ids.product_id:
                    product_quant = rec.quant_ids.filtered(
                        lambda x: x.quantity > 0 and x.product_id == product
                    )
                    if len(product_quant) > 1:
                        raise UserError(
                            _(
                                "You cannot convert this location into a flowable location"
                                " because there are unmixed products."
                            )
                        )
                    if product.uom_id.id != vals.get(
                        "flowable_uom_id", rec.flowable_uom_id
                    ):
                        raise UserError(
                            _(
                                "You cannot convert this location into a flowable location"
                                " because there are products with different units of"
                                " measure."
                            )
                        )
            elif not vals.get("flowable_storage", True):
                vals.update(
                    {
                        "flowable_sequence_id": False,
                        "flowable_allowed_product_ids": False,
                        "flowable_capacity": 0,
                        "flowable_uom_id": False,
                    }
                )
            res = super(Location, rec).write(vals)
            if rec.flowable_storage:
                removed_product_ids = set(old_allowed_products.ids) - set(
                    rec.flowable_allowed_product_ids.ids
                )
                for product_id in removed_product_ids:
                    if rec.quant_ids.filtered(
                        lambda x: x.product_id.id == product_id and x.quantity > 0
                    ):
                        raise UserError(
                            _(
                                "You cannot remove a product that is currently"
                                " stored in this location."
                            )
                        )
        return res
