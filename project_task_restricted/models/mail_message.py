# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MailMessage(models.Model):
    _inherit = "mail.message"

    # for the record rule on notifications, which every internal user can list
    restricted = fields.Boolean(
        compute="_compute_restricted",
        search="_search_restricted",
        groups="project_task_restricted.group_restricted_task",
    )

    def _compute_restricted(self):
        for message in self:
            message.restricted = bool(message._restricted_task())

    def _search_restricted(self, operator, value):
        return self.env["project.task"]._restricted_reference_search(
            "model", "res_id", operator, value
        )

    @api.model_create_multi
    def create(self, vals_list):
        """Every message is created here, whatever produces it. One about a
        marked task keeps only the addressees the task allows."""
        messages = super().create(vals_list)
        for message in messages:
            message._restricted_task()._restricted_address(message)
        return messages

    @api.constrains("parent_id", "model", "res_id")
    def _check_restricted_parent(self):
        """Discuss shows a reply's parent formatted as superuser, so a marked
        task's message is the parent only of messages about the same task."""
        for message in self:
            task = message.parent_id._restricted_task()
            if task and message._restricted_task() != task:
                raise ValidationError(
                    _(
                        "A message of a restricted task can only be answered "
                        "on that task."
                    )
                )

    def _restricted_task(self):
        """The marked task this message is about, or an empty recordset, also
        for no message."""
        if not self:
            return self.env["project.task"]
        self.ensure_one()
        message = self.sudo()
        return self.env["project.task"]._restricted_task_of(
            message.model, message.res_id
        )
