# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_confirmation_values(self):
        res = super()._prepare_confirmation_values()
        for rec in self:
            if rec.date_order:
                res["date_order"] = rec.date_order
        return res
