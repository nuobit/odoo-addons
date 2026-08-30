# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        return ["id", *super()._prepare_merge_moves_distinct_fields()]
