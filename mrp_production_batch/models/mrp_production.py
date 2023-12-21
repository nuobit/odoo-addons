# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_ready_to_produce = fields.Boolean(
        store=True,
        readonly=False,
    )
    error_message = fields.Char()
    production_batch_id = fields.Many2one(
        comodel_name="mrp.production.batch",
        string="Production Batch",
        ondelete="restrict",
        domain="[('state', '!=', 'done')]",
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
                    if not self.env.context.get("mrp_production_batch_create"):
                        raise ValidationError(
                            _(
                                "You can't change the state of a production %s "
                                "because it belongs to a batch: %s.\n"
                                "It must be processed from the batch."
                            )
                            % (rec.name, rec.production_batch_id.name)
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
        picking_type_ids = mrp_productions.picking_type_id
        if len(picking_type_ids) > 1:
            raise ValidationError(
                _(
                    "Some of the selected productions have different picking types:%s"
                    % picking_type_ids.mapped("name")
                )
            )

    def mrp_production_batch_create_wizard_action(self):
        model = self.env.context.get("active_model")
        mrp_production_ids = self.env[model].browse(self.env.context.get("active_ids"))
        self._check_production_to_batch_consistency(mrp_production_ids)
        ctx = dict(self.env.context, active_ids=self.ids)

        view_form = self.env.ref(
            "mrp_production_batch.wizard_mrp_production_batch_view_form"
        )
        res_id = self.env["mrp.production.batch.wizard"].create(
            {
                "warehouse_id": mrp_production_ids.mapped("picking_type_id")
                .mapped("warehouse_id")
                .id,
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
            "context": ctx,
        }
        return res

    def _action_generate_consumption_wizard(self, consumption_issues):
        if not self.env.context.get("mrp_production_batch_create"):
            return super()._action_generate_consumption_wizard(consumption_issues)
        else:
            raise ValidationError(
                _(
                    "Production %s have not recorded produced quantities yet."
                    % self.mapped("name")
                )
            )

    def _action_generate_immediate_wizard(self):
        if not self.env.context.get("mrp_production_batch_create"):
            return super()._action_generate_immediate_wizard()
        else:
            raise ValidationError(
                _(
                    "Production %s have not recorded produced quantities yet."
                    % self.mapped("name")
                )
            )

    # TODO: xml action
    def action_view_production_batch(self):
        self.ensure_one()
        view = self.env.ref("mrp_production_batch.mrp_production_batch_form_view")
        return {
            "name": _("Detailed Operations"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mrp.production.batch",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "res_id": self.production_batch_id.id,
        }

    def action_check_production_with_batch(self):
        self.ensure_one()
        self.production_batch_id.with_context(mrp_production_check=True).action_check()
