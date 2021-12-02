# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):
        for rec in self:
            super(SaleOrder, rec).action_confirm()
            self._event("on_confirm_order").notify(rec)

        return True

    @api.multi
    def action_cancel(self):
        for rec in self:
            super(SaleOrder, rec).action_cancel()
            self._event("on_cancel_order").notify(rec)

        return True
