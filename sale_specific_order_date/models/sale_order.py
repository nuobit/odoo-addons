# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_confirmation_values(self):
        res = super()._prepare_confirmation_values()
        if self.date_order:
            res["date_order"] = self.date_order
        return res
