# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import UserError


class Lead(models.Model):
    _inherit = "crm.lead"

    def toggle_active(self):
        res = super(Lead, self).toggle_active()
        activated = self.filtered(lambda lead: lead.active)
        if activated:
            new_stage_id = self.env.context.get("force_stage_id", False)
            activated.write({"stage_id": new_stage_id})
        return res

    def _find_stage_lost(self):
        lost_stage = self.env["crm.stage"].search([("is_lost", "=", True)])
        if not lost_stage:
            raise UserError(
                _(
                    "There is no lost stage defined. Please define one in the settings menu."
                )
            )
        return lost_stage

    def action_set_lost(self, **additional_values):
        lost_stage = self._find_stage_lost()
        return super().action_set_lost(
            **{**additional_values, "stage_id": lost_stage.id}
        )

    def write(self, vals):
        old_leads_stage = {x: x.stage_id for x in self}
        res = super(Lead, self).write(vals)
        if "stage_id" in vals:
            for rec in self:
                old_stage, new_stage = old_leads_stage[rec], rec.stage_id
                if new_stage and old_stage and new_stage != old_stage:
                    if new_stage.is_lost and not old_stage.is_lost:
                        rec.action_set_lost()
                    elif not new_stage.is_lost and old_stage.is_lost:
                        rec.with_context(force_stage_id=new_stage.id).toggle_active()
        return res
