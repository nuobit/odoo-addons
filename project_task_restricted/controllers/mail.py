# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.mail.controllers import discuss


class DiscussController(discuss.DiscussController):
    @http.route()
    def mail_message_post(self, thread_model, thread_id, post_data, **kwargs):
        # the chatter composer: a person typed these recipients in
        request.context = dict(
            request.context,
            restricted_typed_partner_ids=post_data.get("partner_ids", []),
        )
        return super().mail_message_post(thread_model, thread_id, post_data, **kwargs)
