# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import pytz

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    date_order_tz = fields.Date(
        string="Order Date TZ", readonly=True, compute="_compute_date_order_tz"
    )

    def _compute_date_order_tz(self):
        user_tz = pytz.timezone(self.env.user.tz or "GMT")
        for order in self:
            datetime_utc = pytz.utc.localize(order.date_order)
            datetime_local = datetime_utc.astimezone(user_tz)
            order.date_order_tz = datetime_local.date()

    service_date_tz = fields.Date(compute="_compute_service_date_tz")

    def _compute_service_date_tz(self):
        for rec in self:
            rec.service_date_tz = fields.Date.context_today(rec, rec.service_date)
