# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class QueueJob(models.Model):
    _inherit = "queue.job"

    def _change_job_state(self, state, result=None):
        # queue_job saves the new state as superuser: check the caller's write access
        self.check_access_rights("write")
        self.check_access_rule("write")
        return super()._change_job_state(state, result=result)
