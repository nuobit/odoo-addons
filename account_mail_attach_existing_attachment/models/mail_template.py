# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def _generate_template(self, res_ids, render_fields, find_or_create_partners=False):
        res = super()._generate_template(
            res_ids, render_fields, find_or_create_partners=find_or_create_partners
        )

        if not self.env.context.get("skip_account_mail_attachments", False):
            multi_mode = True
            if isinstance(res_ids, int):
                res_ids = [res_ids]
                multi_mode = False

            if self.model not in ["account.move"]:
                return res

            moves = self.env[self.model].browse(res_ids)
            if not moves or moves.filtered(lambda x: x.move_type != "out_invoice"):
                return res

            for move in moves:
                attachments = self.env["ir.attachment"].search(
                    [("res_model", "=", "account.move"), ("res_id", "=", move.id)]
                )
                move_data = res[move.id] if multi_mode else res
                move_data.setdefault("attachments", [])
                existing_checksums = {
                    self.env["ir.attachment"]._compute_checksum(attachment_data)
                    for attachment_name, attachment_data in move_data["attachments"]
                }
                for attachment in attachments:
                    checksum = self.env["ir.attachment"]._compute_checksum(
                        attachment.datas
                    )
                    if checksum not in existing_checksums:
                        move_data["attachments"].append(
                            (attachment.name, attachment.datas)
                        )
        return res
