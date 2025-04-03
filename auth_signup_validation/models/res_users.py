# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, models
from odoo.osv.expression import AND, OR

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    def action_reset_password_extended(self):
        return {
            "default": super().action_reset_password,
        }

    def action_reset_password(self):
        auth_signup_method = self.env.context.get("auth_signup_method", False)
        if auth_signup_method:
            if auth_signup_method == "all":
                results = {}
                for method, function in self.action_reset_password_extended().items():
                    results[method] = function()
                return results
            function = self.action_reset_password_extended().get(
                auth_signup_method, self.action_reset_password_extended()["default"]
            )
            return function()
        return super().action_reset_password()

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
        domain = [("user_ids", "=", False)]
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
        if self.env.context.get("auth_signup_method"):
            email = values.get("email")
            # TODO: El mobile en aquest punt encara no esta afegit al signup
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
        return super()._signup_create_user(values)
