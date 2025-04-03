# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def generate_email(self, res_ids, fields):
        if self.env.context.get("auth_signup_method", False) in ["email", "all"]:
            self = self.with_context(auth_signup_email="email")
        return super(MailTemplate, self).generate_email(res_ids, fields)
