# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    message_binary_attachment_count = fields.Integer(
        string="Binary Attachment Count",
        compute="_compute_binary_message_attachment_count",
        groups="base.group_user",
    )

    def _compute_binary_message_attachment_count(self):
        read_group_var = self.env["ir.attachment"].read_group(
            [
                ("res_id", "in", self.ids),
                ("res_model", "=", self._name),
                ("type", "=", "binary"),
            ],
            fields=["res_id"],
            groupby=["res_id"],
        )

        attachment_count_dict = {d["res_id"]: d["res_id_count"] for d in read_group_var}
        for record in self:
            record.message_binary_attachment_count = attachment_count_dict.get(
                record.id, 0
            )
