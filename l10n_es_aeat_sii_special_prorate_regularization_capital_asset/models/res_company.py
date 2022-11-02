# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

import pytz

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    capital_asset_use_connector = fields.Boolean(
        string="Use connector",
        help="Check it to use connector instead of sending the invoice "
        "directly when it's validated",
    )
    capital_asset_send_mode = fields.Selection(
        string="Send mode",
        selection=[
            ("auto", "On validate"),
            ("fixed", "At fixed time"),
            ("delayed", "With delay"),
        ],
        default="auto",
    )
    capital_asset_sent_time = fields.Float(
        string="Sent time",
    )
    capital_asset_delay_time = fields.Float(
        string="Delay time",
    )

    # TODO: This code is like _get_sii_eta. Refactor and fix bugs in fixed mode and make an a PR
    def _get_sii_eta_capital_assets(self):
        if self.capital_asset_send_mode == "fixed":
            tz = self.env.context.get("tz", self.env.user.partner_id.tz)
            offset = datetime.now(pytz.timezone(tz)).strftime("%z") if tz else "+00"
            hour_diff = int(offset[:3])
            hour, minute = divmod(self.capital_asset_sent_time * 60, 60)
            hour = int(hour - hour_diff)
            minute = int(minute)
            now = datetime.now()
            if now.hour > hour or (now.hour == hour and now.minute > minute):
                now += timedelta(days=1)
            now = now.replace(hour=hour, minute=minute)
            return now
        elif self.send_mode == "delayed":
            return datetime.now() + timedelta(
                seconds=self.capital_asset_delay_time * 3600
            )
        else:
            return None
