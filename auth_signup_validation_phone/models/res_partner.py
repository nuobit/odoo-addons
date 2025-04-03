# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

from odoo.addons.auth_signup.models.res_partner import random_token

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    signup_mobile_validated = fields.Boolean(
        compute="_compute_signup_mobile_validated",
        inverse="_inverse_signup_mobile_validated",
        readonly=False,
    )

    def _compute_signup_mobile_validated(self):
        for rec in self:
            if rec.auth_method_validated:
                rec.signup_mobile_validated = rec.auth_method_validated.get(
                    "mobile", False
                )
            else:
                rec.signup_mobile_validated = False

    def _inverse_signup_mobile_validated(self):
        for rec in self:
            auth_vals = rec.auth_method_validated or {}
            auth_vals["mobile"] = rec.signup_mobile_validated
            rec.auth_method_validated = auth_vals

    def write(self, vals):
        if "auth_method_token" in vals:
            auth_method_token = vals["auth_method_token"]
            if self.auth_method_token:
                if self.auth_method_token.get("mobile") and not auth_method_token.get(
                    "mobile"
                ):
                    m_validated = (
                        vals.get("auth_method_validated", self.auth_method_validated)
                    ) | {"mobile": True}
                    vals["auth_method_validated"] = m_validated
        auth_method_validated = vals.get("auth_method_validated")
        if auth_method_validated and auth_method_validated.get("mobile"):
            auth_method_token = vals.get("auth_method_token", self.auth_method_token)
            if auth_method_token and auth_method_token.get("mobile"):
                auth_method_token.pop("mobile")
                vals["auth_method_token"] = auth_method_token
        return super().write(vals)

    @api.model
    def signup_retrieve_info(self, token):
        res = super().signup_retrieve_info(token)
        partner = self._signup_retrieve_partner(token, raise_exception=True)
        if partner.signup_valid:
            res.update({"mobile": partner.mobile})
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
        for p in self:
            if res.get(p.id):
                if self.env.context.get("auth_signup_mobile"):
                    m_validated = (p.auth_method_validated or {}) | {"mobile": False}
                    vals = {"auth_method_validated": m_validated}
                    if self.env.context.get("auth_signup_method") == "all":
                        token = random_token()
                        m_token = (p.auth_method_token or {}) | {"mobile": token}
                        vals.update({"auth_method_token": m_token})
                        res[p.id] += f"&auth_signup={token}"
                    p.write(vals)
        return res
