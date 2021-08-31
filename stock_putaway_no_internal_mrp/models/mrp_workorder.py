# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.workorder"

    def _update_finished_move(self):
        return super(
            MrpProduction,
            self.with_context(stock_picking_type_code=self.picking_type_id.code),
        ).open_produce_product()
