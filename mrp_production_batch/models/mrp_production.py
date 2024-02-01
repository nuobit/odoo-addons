# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class FakeException(ValidationError):
    pass


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_ready_to_produce = fields.Boolean(copy=False)
    error_message = fields.Char(copy=False)
    production_batch_id = fields.Many2one(
        comodel_name="mrp.production.batch",
        string="Production Batch",
        copy=False,
        ondelete="restrict",
        domain="[('state', '!=', 'done')]",
    )

    @api.constrains("lot_producing_id")
    def _check_lot_producing_by_batch(self):
        for rec in self:
            if not self.env.context.get("mrp_production_batch_create"):
                if rec.lot_producing_id and rec.production_batch_id:
                    raise ValidationError(
                        _(
                            "You can't set a lot producing for a production %s "
                            "that belongs to a batch: %s.\n"
                            "It must be processed from the batch."
                        )
                        % (rec.name, rec.production_batch_id.name)
                    )

    @api.constrains("production_batch_id")
    def _check_production_batch(self):
        for rec in self:
            if rec.lot_producing_id:
                raise ValidationError(
                    _(
                        "You can't set a production batch for a production %s "
                        "because it has a lot/serial number."
                    )
                    % rec.name
                )

    @api.constrains("state")
    def _check_state_batch_creation(self):
        for rec in self:
            if rec.production_batch_id:
                if rec.state == "cancel":
                    raise ValidationError(
                        _(
                            "You can't cancel a production that belongs to a batch %s. "
                            "Please, delete it from the batch first."
                        )
                        % rec.production_batch_id.name
                    )
                elif rec.state == "done":
                    if (
                        not self.env.context.get("mrp_production_batch_create", False)
                        and not rec.scrap_ids
                    ):
                        raise ValidationError(
                            _(
                                "You can't change the state of a production %s "
                                "because it belongs to a batch: %s.\n"
                                "It must be processed from the batch."
                            )
                            % (rec.name, rec.production_batch_id.name)
                        )

    @api.constrains("production_batch_id")
    def _check_operation_type(self):
        for rec in self:
            if (
                rec.picking_type_id.warehouse_id
                != rec.production_batch_id.operation_type.warehouse_id
            ):
                raise ValidationError(
                    _(
                        "The warehouse of the batch must be the same"
                        " as the warehouse of the productions."
                    )
                )

    def _check_production_to_batch_consistency(self, mrp_productions):
        if not mrp_productions:
            raise ValidationError(_("No productions selected"))
        if mrp_productions.production_batch_id:
            raise ValidationError(
                _("Some of the selected productions already have a batch")
            )
        if {"done", "cancel"} & set(mrp_productions.mapped("state")):
            raise ValidationError(
                _("Some of the selected productions are already done or cancelled")
            )
        if len(mrp_productions.picking_type_id) > 1:
            raise ValidationError(
                _("Some of the selected productions have different operation types")
            )
        if len(mrp_productions.picking_type_id.warehouse_id) > 1:
            raise ValidationError(
                _("Some of the selected productions have different warehouses")
            )
        if len(mrp_productions.picking_type_id) > 1:
            raise ValidationError(
                _(
                    "Some of the selected productions have different picking types:%s"
                    % mrp_productions.picking_type_id.mapped("name")
                )
            )

    def mrp_production_batch_create_wizard_action(self):
        if (
            "active_model" not in self.env.context
            or "active_ids" not in self.env.context
        ):
            raise ValidationError(
                _(
                    "An unexpected error has occurred. There's no `active_model` or "
                    "`active_ids` in the context. This is a technical error, please "
                    "contact technical support."
                )
            )
        model, active_ids = [
            self.env.context.get(x) for x in ["active_model", "active_ids"]
        ]
        mrp_production_ids = self.env[model].browse(active_ids)
        self._check_production_to_batch_consistency(mrp_production_ids)
        view_form = self.env.ref(
            "mrp_production_batch.mrp_production_batch_wizard_view_form"
        )
        res_id = self.env["mrp.production.batch.wizard"].create(
            {
                "warehouse_id": mrp_production_ids.picking_type_id.warehouse_id.id,
            }
        )
        res = {
            "name": _("MRP production Batch"),
            "view_mode": "form",
            "res_model": "mrp.production.batch.wizard",
            "res_id": res_id.id,
            "target": "new",
            "views": [(view_form.id, "form")],
            "view_id": view_form.id,
            "type": "ir.actions.act_window",
            "context": dict(self.env.context, active_ids=self.ids),
        }
        return res

    def _action_generate_consumption_wizard(self, consumption_issues):
        if not self.env.context.get("mrp_production_batch_create"):
            return super()._action_generate_consumption_wizard(consumption_issues)
        if self.bom_id.bom_line_ids.product_id != self.move_raw_ids.product_id:
            raise ValidationError(
                _(
                    "A problem has been detected in production %s. Make sure you "
                    "have added all the necessary components from the materials "
                    "list. Please check this and, once corrected, try again."
                )
                % self.mapped("name")
            )
        else:
            raise ValidationError(
                _(
                    "A problem has been detected in production %s. Verify that the"
                    " quantities to be consumed are indicated correctly. Please "
                    "check this and, once corrected, try again."
                )
                % self.mapped("name")
            )

    def _action_generate_immediate_wizard(self):
        if not self.env.context.get("mrp_production_batch_create"):
            return super()._action_generate_immediate_wizard()
        raise ValidationError(
            _(
                "Production %s have not recorded produced quantities yet."
                % self.mapped("name")
            )
        )

    # TODO: xml action
    def action_view_production_batch(self):
        self.ensure_one()
        view = self.env.ref("mrp_production_batch.mrp_production_batch_view_form")
        return {
            "name": _("Detailed Operations"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mrp.production.batch",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "res_id": self.production_batch_id.id,
        }

    def action_produce_batch(self):
        for rec in self:
            try:
                with rec.env.cr.savepoint():
                    self_wc = rec.with_context(mrp_production_batch_create=True)
                    lot = self_wc.env["stock.production.lot"].create(
                        {
                            "name": "",
                            "product_id": rec.product_id.id,
                            "company_id": rec.company_id.id,
                        }
                    )
                    self_wc.lot_producing_id = lot.id
                    self_wc.button_mark_done()
                    raise FakeException("")
            except FakeException:
                rec.is_ready_to_produce = True
                rec.error_message = False
            except (UserError, ValidationError) as e:
                rec.is_ready_to_produce = False
                rec.error_message = e.name

    def create_batch_lot_by_bom(self):
        self.ensure_one()
        if not self.bom_id:
            raise ValidationError(
                _(
                    "Bill of Materials is required for the production. "
                    "Please unbind the batch production."
                )
            )

        batch_component = self.bom_id.bom_line_ids.filtered(
            lambda x: x.use_in_batch
        ).product_id
        if not batch_component:
            raise ValidationError(
                _("Please assign a batch compatible product in the Bill of Materials")
            )
        component_lot = False
        for line in self.move_raw_ids.move_line_ids:
            if line.product_id == batch_component:
                component_lot = line.lot_id
        if not component_lot:
            raise ValidationError(
                _(
                    "No compatible batch product found in the material list."
                    " Ensure a product marked for batch use is included."
                )
            )
        batch_sequence = (
            self.env["res.company"]
            .browse(self.company_id.id)
            .sequence_production_batch_id.next_by_id()
        )
        return component_lot.name + batch_sequence

    def action_generate_batch_serial(self):
        self.ensure_one()
        seq_name = self.create_batch_lot_by_bom()
        self.lot_producing_id = self.env["stock.production.lot"].create(
            {
                "name": seq_name,
                "product_id": self.product_id.id,
                "company_id": self.company_id.id,
            }
        )

    def write(self, values):
        if "production_batch_id" in values and not values["production_batch_id"]:
            values["is_ready_to_produce"] = False
            values["error_message"] = False
        return super().write(values)
