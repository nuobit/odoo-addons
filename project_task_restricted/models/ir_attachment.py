# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def generate_access_token(self):
        """An attachment of a marked task gets no download link: whoever held
        it would download the file as superuser, member or not. The portal
        asks for one whenever it shows the task's page or one of its
        messages; there the link carries no token, and the download is
        allowed to whoever can read the task."""
        Task = self.env["project.task"]
        return [
            None
            if Task._restricted_task_of(attachment.res_model, attachment.res_id)
            else super(IrAttachment, attachment).generate_access_token()[0]
            for attachment in self
        ]
