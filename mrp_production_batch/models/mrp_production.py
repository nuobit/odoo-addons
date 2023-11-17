# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    production_batch_id = fields.Many2one(
        comodel_name="mrp.production.batch",
        string="Production Batch",
        readonly=True,
    )

    def _check_production_to_batch_consitency(self, mrp_production_ids):
        if not mrp_production_ids:
            raise ValidationError(_("No productions selected"))
        if mrp_production_ids.mapped("production_batch_id"):
            raise ValidationError(
                _("Some of the selected productions already have a batch")
            )
        if any(
            state in ("done", "cancel") for state in mrp_production_ids.mapped("state")
        ):
            raise ValidationError(
                _("Some of the selected productions are already done or cancelled")
            )
        picking_type_ids = mrp_production_ids.mapped("picking_type_id")
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
        self._check_production_to_batch_consitency(mrp_production_ids)
        self.env["mrp.production.batch"].create(
            {
                "creation_date": str(fields.Datetime.now()),
                "production_ids": [
                    (6, 0, mrp_production_ids.ids),
                ],
            }
        )

    @api.constrains("state")
    def _check_state_batch_creation(self):
        for rec in self:
            if rec.state == "cancel":
                if rec.production_batch_id:
                    raise ValidationError(
                        _(
                            "You can't cancel a production that belongs to a batch %s. "
                            "Please, delete it from the batch first."
                        )
                        % rec.production_batch_id.name
                    )
            elif rec.state == "done":
                if rec.production_batch_id and not self.env.context.get("batch_create"):
                    raise ValidationError(
                        _(
                            "You can't change the state of a production %s "
                            "because it belongs to a batch: %s. \n "
                            "It must be processed from the batch."
                        )
                        % (rec.name, rec.production_batch_id.name)
                    )

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
