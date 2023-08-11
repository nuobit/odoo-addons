# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Stage(models.Model):
    _inherit = "crm.stage"

    is_lost = fields.Boolean(string="Is Lost Stage?")

    @api.constrains("is_lost")
    def _check_is_lost(self):
        for rec in self:
            others = self.env[self._name].search(
                [("is_lost", "=", True), ("id", "!=", rec.id)]
            )
            if rec.is_lost and others:
                raise ValidationError(
                    _("There is already a lost stage defined: %s")
                    % others.mapped("name")
                )
            leads = (
                self.env["crm.lead"]
                .with_context(active_test=False)
                .search([("stage_id", "=", rec.id)])
            )
            if rec.is_lost:
                leads_non_lost = leads.filtered(lambda l: l.active)
                if leads_non_lost:
                    raise ValidationError(
                        _(
                            "There are leads in non lost state. "
                            "Please move them to another stage before marking "
                            "this stage as lost."
                        )
                    )
            else:
                leads_lost = leads.filtered(lambda l: not l.active)
                if leads_lost:
                    raise ValidationError(
                        _(
                            "There are leads in lost state. "
                            "Please move them to another stage before marking "
                            "this stage as non lost."
                        )
                    )
