# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class MailWizardInvite(models.TransientModel):
    _inherit = "mail.wizard.invite"

    def add_followers(self):
        # without this refusal, the non-members would simply not be added
        for wizard in self:
            self.env["project.task"]._restricted_refuse_partners(
                wizard.res_model,
                wizard.res_id,
                wizard.partner_ids,
                wizard._restricted_refusal,
            )
        return super().add_followers()

    def _restricted_refusal(self, task, outsiders):
        return _(
            "Only members of the Restricted tasks group can follow the "
            'restricted task "%(task)s". Not in the group: %(partners)s. '
            "Remove them from the recipients.",
            task=task.name,
            partners=", ".join(outsiders.mapped("name")),
        )
