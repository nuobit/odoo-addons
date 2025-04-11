# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import AND, OR

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _get_partner_priority_cases(self):
        return [
            (True, True),  # Both Email and Mobile match
            (True, None),  # Email matches, Mobile empty in DB
            (True, False),  # Email matches, Mobile differs
            (None, True),  # Email empty in DB, Mobile matches
            (False, True),  # Email differs, Mobile matches
        ]

    @api.model
    def _partner_search_conditions(self):
        return {
            "email": "email",
            "mobile": "mobile",
            "phone": "mobile",
        }

    def _find_partner_candidates(self, values):
        domain = [("user_id", "=", False)]
        search_fields = self._partner_search_conditions()
        conditions = []
        for key, field in search_fields.items():
            value = values.get(field)
            if value:
                conditions.append([(key, "=", value)])
        if conditions:
            domain = AND([OR(conditions), domain])
        return (
            self.env["res.partner"]
            .with_context(active_test=False)
            .search(domain, order="id desc")
        )

    def _sort_priorized_candidates(self, candidates):
        return sorted(
            candidates,
            key=lambda x: (
                not x[1].active,
                x[0],
                -x[1]._count_fields_informed(),
                x[1].id,
            ),
        )

    def _prioritize_partners(self, partners, email, mobile):
        cases = self._get_partner_priority_cases()
        key_new = (email, mobile)
        candidates = []
        for partner in partners:
            key_cur = (partner.email, partner.mobile)
            key = tuple(
                None if not cur else new == cur for cur, new in zip(key_cur, key_new)
            )
            priority = cases.index(key) if key in cases else len(cases)
            candidates.append((priority, partner))
        candidates = self._sort_priorized_candidates(candidates)
        return [(x[0], x[1]) for x in candidates]

    def _archive_duplicate_partners(self, candidates):
        partners_to_archive = self.env["res.partner"]
        for _k, partner in candidates[1:]:
            if partner.active:
                partners_to_archive |= partner
        if partners_to_archive:
            partners_to_archive.write({"active": False})
            _logger.info(
                "Archived duplicate partners: %s", [p.id for p in partners_to_archive]
            )

    def _update_selected_partner(self, partner, values):
        updates = {}
        for field in ["email", "mobile"]:
            new_value = values.get(field)
            if new_value and partner[field] != new_value:
                updates[field] = new_value
        if updates:
            partner.write(updates)
            _logger.info("Updated partner %s with values %s", partner.id, updates)

    @api.model
    def _signup_create_user(self, values):
        if "language" in values:
            values["lang"] = values.pop("language")
        if self.env.context.get("multi_auth_signup"):
            email = values.get("email")
            mobile = values.get("mobile")
            partners = self._find_partner_candidates(values)
            if partners:
                candidates = self._prioritize_partners(partners, email, mobile)
                if candidates:
                    selected_partner = candidates[0][1]
                    self._archive_duplicate_partners(candidates)
                    self._update_selected_partner(selected_partner, values)
                    if not selected_partner.active:
                        selected_partner.active = True
                    values["partner_id"] = selected_partner.id
                    values.pop("name")
        return super()._signup_create_user(values)

    @api.model
    def _format_mobile_number(self, mobile):
        mobile = mobile.strip().replace(" ", "")
        if mobile.startswith("+"):
            mobile = mobile[1:]
        return mobile

    def _get_channel_values(self, gateway):
        mobile = self._format_mobile_number(self.mobile)
        return {
            "metadata": {"phone_number_id": gateway.whatsapp_from_phone},
            "contacts": [{"profile": {"name": self.name}, "wa_id": mobile}],
            "messages": [{"from": gateway.whatsapp_from_phone, "to": mobile}],
        }

    def _validate_and_get_whatsapp_channel(self):
        lang = self.env.context.get("web_lang", self.env.lang)
        bot_data = (
            self.env["mail.gateway"]
            .with_context(lang=lang)
            ._get_default_registration_gateway()
        )

        dispatcher = self.env["mail.gateway.whatsapp"].with_user(
            bot_data["webhook_user_id"]
        )
        gateway = dispatcher.env["mail.gateway"].browse(bot_data["id"])
        if not gateway:
            raise ValidationError(_("No WhatsApp gateway configured for verification."))
        if not self.mobile:
            raise ValidationError(_("Phone number is required for verification."))

        chat = dispatcher._get_channel(
            gateway,
            self._format_mobile_number(self.mobile),
            self._get_channel_values(gateway),
            force_create=True,
        )

        lang = self.env["res.lang"].search([("code", "=", lang)], limit=1)
        template_id = bot_data["default_template_by_lang"].get(
            lang.iso_code
        ) or bot_data["default_template_by_lang"].get(lang.code)
        if not template_id:
            raise ValidationError(
                _("WhatsApp template not found for the language %s.") % lang.name
            )

        whatsapp_template = self.env["mail.whatsapp.template"].browse(template_id)
        if not whatsapp_template.exists():
            raise ValidationError(_("WhatsApp template doesn't exist or was deleted."))

        return chat, whatsapp_template

    def _get_template_variables(self, whatsapp_template):
        variables_values = {"body": {}}
        for variable in whatsapp_template.variable_ids.filtered(
            lambda x: x.section == "body"
        ):
            field_name = variable.signup_field_id.name
            if not field_name:
                raise ValidationError(
                    _("The WhatsApp template lacks a signup field for %s.")
                    % variable.name
                )

            if field_name == "signup_url":
                self = self.with_context(auth_signup_phone=True)

            variables_values["body"][variable.name] = self[field_name]

        return variables_values

    def send_whatsapp_message(self):
        chat, whatsapp_template = self._validate_and_get_whatsapp_channel()
        variables_values = self._get_template_variables(whatsapp_template)
        body = whatsapp_template.with_context(
            variables_values=variables_values
        ).get_body()
        return chat.with_context(
            whatsapp_template_id=whatsapp_template.id, variables_values=variables_values
        ).message_post(
            body=body,
            author_id=False,
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            date=fields.Datetime.now(),
            raise_exception=True,
        )

    def action_reset_password(self):
        if not self.env.context.get("multi_auth_signup"):
            return super().action_reset_password()

        super().action_reset_password()
        self.mapped("partner_id").signup_prepare(signup_type="reset")

        # Ensure the transaction is committed before sending the msg, in case it fails
        try:
            with self.env.cr.savepoint():
                return self.send_whatsapp_message()
        except Exception as e:
            _logger.error("Failed to send WhatsApp message: %s", e)
            return False
