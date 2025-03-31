# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

from odoo.addons.auth_signup.models.res_partner import random_token

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    signup_mobile_validated = fields.Boolean(
        copy=False, tracking=True, string="Mobile Validated"
    )
    signup_mobile_token = fields.Char(copy=False)
    signup_email_validated = fields.Boolean(
        copy=False, tracking=True, string="Email Validated"
    )
    signup_email_token = fields.Char(copy=False)

    @api.model
    def signup_retrieve_info(self, token):
        res = super().signup_retrieve_info(token)
        partner = self._signup_retrieve_partner(token, raise_exception=True)
        if partner.signup_valid:
            res.update({"mobile": partner.mobile, "language": partner.lang})
        return res

    def _get_signup_url_for_action(
        self,
        url=None,
        action=None,
        view_type=None,
        menu_id=None,
        res_id=None,
        model=None,
    ):
        res = super()._get_signup_url_for_action(
            url=url,
            action=action,
            view_type=view_type,
            menu_id=menu_id,
            res_id=res_id,
            model=model,
        )
        for partner in self:
            if res.get(partner.id):
                token = random_token()
                if self.env.context.get("auth_signup_email"):
                    partner.write(
                        {"signup_email_token": token, "signup_email_validated": False}
                    )
                    res[partner.id] += f"&auth_signup={token}"
                elif self.env.context.get("auth_signup_phone"):
                    partner.write(
                        {"signup_mobile_token": token, "signup_mobile_validated": False}
                    )
                    res[partner.id] += f"&auth_signup={token}"
        return res

    def _count_fields_informed(self):
        stored_fields = [
            name
            for name, field in self._fields.items()
            if field.store and not field.compute
        ]
        return sum(bool(self[field]) for field in stored_fields)
