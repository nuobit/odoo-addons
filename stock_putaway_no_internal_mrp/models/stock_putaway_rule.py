# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockPutawayRule(models.Model):
    _inherit = "stock.putaway.rule"

    def _excluded_picking_types(self):
        return super()._excluded_picking_types() + ["mrp_operation"]
