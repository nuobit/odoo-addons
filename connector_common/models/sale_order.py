# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        for rec in self:
            super(SaleOrder, rec).action_confirm()
            self._event("on_confirm_order").notify(rec)
        return True

    def action_cancel(self):
        for rec in self:
            super(SaleOrder, rec).action_cancel()
            self._event("on_cancel_order").notify(rec)
        return True
