# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MailNotification(models.Model):
    _inherit = "mail.notification"

    def send_gateway(self, auto_commit=False, raise_exception=False, parse_mode="HTML"):
        if self.env.context.get("auth_signup_phone"):
            raise_exception = True
        return super().send_gateway(
            auto_commit=auto_commit,
            raise_exception=raise_exception,
            parse_mode=parse_mode,
        )
