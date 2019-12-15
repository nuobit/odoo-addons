# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        for rec in self:
            self._event("on_confirm_order").notify(rec)
        return res

    def action_cancel(self):
        res = super().action_cancel()
        self._event("on_cancel_order").notify(self)
        return res
