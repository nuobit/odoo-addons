# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.osv import expression


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _timesheet_get_portal_domain(self):
        """The portal reads the timesheets as superuser, and for anyone
        outside the Timesheets groups with this domain instead of the record
        rules: there, whoever is outside the Restricted tasks group finds no
        line of a marked task."""
        domain = super()._timesheet_get_portal_domain()
        return (
            domain
            if self.env["project.task"]._restricted_user_is_member()
            else expression.AND(
                [
                    domain,
                    ["|", ("task_id", "=", False), ("task_id.restricted", "=", False)],
                ]
            )
        )
