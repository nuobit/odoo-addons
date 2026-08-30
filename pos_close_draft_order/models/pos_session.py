# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class PosSession(models.Model):
    _inherit = "pos.session"

    def post_closing_cash_details(self, counted_cash):
        orders = self.order_ids.filtered(lambda x: x.state == "draft")
        if orders:
            session = (
                self.env["pos.session"]
                .with_context(allow_multiple_session=True)
                .create(
                    {
                        "user_id": self.env.uid,
                        "config_id": self.config_id.id,
                        "state": "opened",
                    }
                )
            )
            orders.write({"session_id": session.id})
        return super(PosSession, self).post_closing_cash_details(counted_cash)

    @api.constrains("config_id")
    def _check_pos_config(self):
        if not self.env.context.get("allow_multiple_session", False):
            return super(PosSession, self)._check_pos_config()
