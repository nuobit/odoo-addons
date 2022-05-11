# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class StockOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _get_product_context(self):
        res = super(StockOrderpoint, self)._get_product_context()
        # We want to consider all incoming/outgoing moves.
        res.pop("to_date")
        return res
