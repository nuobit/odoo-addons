# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    flowable_production_ids = fields.One2many(
        string="Manufacturing Orders",
        comodel_name="mrp.production",
        inverse_name="picking_id",
    )

    def action_view_mrp_production(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp.mrp_production_action"
        )
        form = self.env.ref("mrp.mrp_production_form_view")
        if len(self.flowable_production_ids) == 1:
            action["views"] = [(form.id, "form")]
            action["res_id"] = self.flowable_production_ids[0].id
        else:
            action["domain"] = [("id", "in", self.flowable_production_ids.ids)]
            action["context"] = {**self.env.context, "search_default_todo": False}
        return action

    def _prepare_lot_values(self, product, location_dest, qty_done):
        self.ensure_one()
        return {
            "name": location_dest.flowable_sequence_id._next(),
            "product_id": product.id,
            "product_qty": qty_done,
            "product_uom_id": product.uom_id.id,
        }

    def _prepare_production_move_line_values(self, move_line, product, location_dest):
        self.ensure_one()
        return {
            "lot_id": move_line.lot_id.id,
            "product_id": product.id,
            "qty_done": move_line.quantity,
            "product_uom_id": product.uom_id.id,
            "location_id": location_dest.id,
            "location_dest_id": product.with_company(
                self.company_id
            ).property_stock_production.id,
        }

    def _prepare_production_move_values(
        self, product, location_dest, quantity_to_prod, mrp_operation_type
    ):
        self.ensure_one()
        return {
            "name": product.name,
            "product_id": product.id,
            "picking_type_id": mrp_operation_type.id,
            "location_id": location_dest.id,
            "location_dest_id": location_dest.id,
            "product_uom": product.uom_id.id,
            "product_uom_qty": quantity_to_prod,
        }

    def _prepare_production_values(
        self, product, location_dest, quantity_to_prod, mrp_operation_type
    ):
        self.ensure_one()
        return {
            "product_id": product.id,
            "product_qty": quantity_to_prod,
            "product_uom_id": product.uom_id.id,
            "picking_type_id": mrp_operation_type.id,
            "location_src_id": location_dest.id,
            "location_dest_id": location_dest.id,
            "picking_id": self.id,
            "move_raw_ids": [
                (
                    0,
                    0,
                    self._prepare_production_move_values(
                        product, location_dest, quantity_to_prod, mrp_operation_type
                    ),
                )
            ],
        }

    def button_validate(self):
        for rec in self:
            if rec.move_line_ids_without_package.filtered(
                lambda x: x.location_dest_id.flowable_storage
                or x.location_id.flowable_storage
            ):
                rec.env.context = dict(rec.env.context)
                rec.env.context["allow_duplicate"] = True
        return super().button_validate()

    def _action_done(self):
        res = super(
            StockPicking,
            self.with_context(flowable_skip_trigger_assign=True),
        )._action_done()
        for rec in self:
            flowable_lines = rec.move_line_ids_without_package.filtered(
                lambda x: x.location_dest_id.flowable_storage
            )
            if not flowable_lines:
                continue

            # checks before creating manufacturing orders
            mrp_operation_type = rec.env["stock.picking.type"].search(
                [
                    ("warehouse_id", "=", rec.picking_type_id.warehouse_id.id),
                    ("code", "=", "mrp_operation"),
                    ("flowable_operation", "=", True),
                ]
            )
            if not mrp_operation_type:
                raise UserError(
                    _(
                        "Not found flowable manufacturing picking type"
                        " in warehouse %s"
                    )
                    % rec.picking_type_id.warehouse_id.name
                )
            elif len(mrp_operation_type) > 1:
                raise UserError(
                    _(
                        "More than one flowable manufacturing picking type"
                        " in warehouse %s"
                    )
                    % rec.picking_type_id.warehouse_id.name
                )
            else:
                if not mrp_operation_type.sequence_id:
                    raise UserError(
                        _(
                            "Not found sequence in flowable manufacturing"
                            " picking type %s"
                        )
                        % mrp_operation_type.display_name
                    )

            # Group move lines by (product, dest location, lot) and check for
            # conflicts. The blocking mechanism would catch this too (the first
            # MO blocks the location, the second hits the constraint), but
            # that error references a phantom MO created in the same rolled-back
            # transaction. Pre-checking here gives an actionable message.
            lines = {}
            for line in flowable_lines:
                key = (line.product_id, line.location_dest_id, line.lot_id)
                lines[key] = lines.get(key, 0) + line.qty_done
                existing = [k for k in lines if k[1] == line.location_dest_id]
                if len(existing) > 1:
                    details = ", ".join(
                        "%s (%s)" % (k[0].name, k[2].name) if k[2] else k[0].name
                        for k in existing
                    )
                    raise UserError(
                        _(
                            "Cannot receive multiple product/lot combinations"
                            " (%s) at flowable location '%s' in the same"
                            " receipt. Each combination generates a separate"
                            " mixing order and the location is blocked after"
                            " the first one. Create a backorder to receive"
                            " them in separate steps."
                        )
                        % (details, line.location_dest_id.name)
                    )

            # create manufacturing orders
            for (product, location_dest, lot), qty_done in lines.items():
                if product not in location_dest.flowable_allowed_product_ids:
                    raise UserError(
                        _("Product %s not allowed in flowable location %s")
                        % (product.name, location_dest.name)
                    )
                if product.uom_id != location_dest.flowable_uom_id:
                    raise UserError(
                        _(
                            "The allowed products %s cannot have different Unit of"
                            " Measure than flowable location %s"
                        )
                        % (product.name, location_dest.name)
                    )
                if product.tracking != "lot":
                    raise UserError(
                        _("Product %s must be tracked by lot") % product.name
                    )
                component_quant = rec.env["stock.quant"].search(
                    [
                        ("product_id", "=", product.id),
                        ("location_id", "=", location_dest.id),
                        ("quantity", ">", 0),
                        ("company_id", "=", rec.company_id.id),
                    ]
                )
                rec._check_flowable_quant_count(
                    component_quant, location_dest, product, lot
                )
                quantity_to_prod = sum(component_quant.mapped("quantity"))
                production = rec.env["mrp.production"].create(
                    rec._prepare_production_values(
                        product, location_dest, quantity_to_prod, mrp_operation_type
                    )
                )
                production._onchange_move_finished_product()
                production._onchange_move_finished()
                production._onchange_location_dest()
                production.action_confirm()
                if location_dest.flowable_create_lots:
                    producing_lot = rec.env["stock.production.lot"].create(
                        rec._prepare_lot_values(product, location_dest, qty_done)
                    )
                else:
                    producing_lot = lot
                vals = []
                for move_line in component_quant:
                    vals.append(
                        (
                            0,
                            0,
                            rec._prepare_production_move_line_values(
                                move_line, product, location_dest
                            ),
                        )
                    )
                production.move_raw_ids.move_line_ids = vals
                production.lot_producing_id = producing_lot
                production.action_assign()
                production.qty_producing = quantity_to_prod
        return res

    def _check_flowable_quant_count(self, quants, location, product, lot):
        is_initial = all(q.lot_id == lot for q in quants)
        if is_initial:
            if len(quants) != 1:
                raise UserError(
                    _(
                        "Initial reception at flowable location '%s'"
                        " for product '%s': expected 1 positive quant"
                        " (empty tank) but found %d."
                    )
                    % (location.name, product.name, len(quants))
                )
        else:
            if len(quants) != 2:
                raise UserError(
                    _(
                        "Mixing reception at flowable location '%s'"
                        " for product '%s': expected 2 positive quants"
                        " but found %d."
                    )
                    % (location.name, product.name, len(quants))
                )
            received = quants.filtered(lambda q: q.lot_id == lot)
            if len(received) != 1:
                raise UserError(
                    _(
                        "Mixing reception at flowable location '%s'"
                        " for product '%s': expected exactly 1 quant"
                        " for the received lot '%s' but found %d."
                    )
                    % (location.name, product.name, lot.name, len(received))
                )
