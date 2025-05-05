# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

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
    resend_since_email = fields.Datetime(
        copy=False, compute="_compute_reset_stats", store=True, readonly=False
    )
    resend_since_mobile = fields.Datetime(
        copy=False, compute="_compute_reset_stats", store=True, readonly=False
    )
    resend_count_mobile = fields.Integer(
        copy=False, compute="_compute_reset_stats", store=True, readonly=False
    )
    resend_count_email = fields.Integer(
        copy=False, compute="_compute_reset_stats", store=True, readonly=False
    )

    @api.depends("user_ids")
    def _compute_reset_stats(self):
        for rec in self:
            rec.resend_since_email = False
            rec.resend_since_mobile = False
            rec.resend_count_email = 0
            rec.resend_count_mobile = 0

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

    @api.model
    def resend_field_mapping(self):
        return {
            "mobile": {
                "field": "resend_count_mobile",
                "since": "resend_since_mobile",
                "max_count": "max_resend_count_mobile",
                "max_delay": "max_resend_delay_mobile",
            },
            "email": {
                "field": "resend_count_email",
                "since": "resend_since_email",
                "max_count": "max_resend_count_email",
                "max_delay": "max_resend_delay_email",
            },
        }

    def update_resend_attempts(self, method):
        self.ensure_one()
        mapping = self.resend_field_mapping().get(method)
        if not mapping:
            raise ValidationError(_("Unknown resend method: %s") % method)

        count_field = mapping["field"]
        since_field = mapping["since"]
        max_count_f = mapping["max_count"]
        max_delay_f = mapping["max_delay"]
        now = fields.Datetime.now()
        company = self.env.company or self.user_ids.company_id
        if self[since_field] and self[count_field] >= company[max_count_f]:
            hours_passed = (now - self[since_field]).total_seconds() / 3600.0
            if hours_passed < company[max_delay_f]:
                raise ValidationError(
                    _(
                        "You can only resend %(count)s %(method)s verification "
                        "messages every %(delay)s hours."
                    )
                    % {
                        "count": company[max_count_f],
                        "method": _(method),
                        "delay": company[max_delay_f],
                    }
                )
            else:
                # If the max delay has passed, reset the resend count
                self[count_field] = 0
                self[since_field] = False
        else:
            self[count_field] = self[count_field] + 1
            self[since_field] = now
        return True

    def action_resend(self, method):
        self.ensure_one()
        users = self.with_context(active_test=False).user_ids
        users.active = True
        users = users.with_context(signup_force_type_in_url="reset", create_user=True)
        if method == "whatsapp":
            users.send_whatsapp_message()
        elif method == "email":
            users.action_reset_password()
        users.active = False

    def action_resend_email(self):
        self.ensure_one()
        self.with_context(auth_signup_email=True).action_resend("email")

    def action_resend_whatsapp(self):
        self.ensure_one()
        self.with_context(auth_signup_phone=True).action_resend("whatsapp")
