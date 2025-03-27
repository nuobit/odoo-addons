# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime

from odoo import _
from odoo.http import request

from odoo.addons.auth_signup.controllers.main import AuthSignupHome

_logger = logging.getLogger(__name__)


class AuthSignupHomePrivacyConsent(AuthSignupHome):
    def _metadata(self):
        return (
            "User agent: {}\n" "Remote IP: {}\n" "Date and time: {:%Y-%m-%d %H:%M:%S}"
        ).format(
            request.httprequest.environ.get("HTTP_USER_AGENT"),
            request.httprequest.environ.get("REMOTE_ADDRESS"),
            datetime.now(),
        )

    def _process_privacy_consent(self, activity, login, answer=True):
        """Common logic to process privacy consent after signup."""
        if not activity:
            return

        User = request.env["res.users"]
        partner = (
            User.sudo()
            .search(
                User._get_login_domain(login), order=User._get_login_order(), limit=1
            )
            .partner_id
        )

        if not partner:
            return

        consent = (
            request.env["privacy.consent"]
            .sudo()
            .search(
                [
                    ("activity_id", "=", activity.id),
                    ("partner_id", "=", partner.id),
                ]
            )
        )
        if not consent:
            consent = (
                request.env["privacy.consent"]
                .with_context(tracking_disable=True)
                .sudo()
                .create(
                    {
                        "activity_id": activity.id,
                        "partner_id": partner.id,
                    }
                )
            )

        body = _("%s consent processed via signup") % activity.name
        consent.message_post(
            body=body,
            subtype_xmlid="mail.mt_comment",
        )
        consent.with_context(subject_answering=True).action_answer(
            answer, self._metadata()
        )
