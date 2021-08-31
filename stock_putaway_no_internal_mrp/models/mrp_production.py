# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from ast import literal_eval

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.multi
    def open_produce_product(self):
        action = super(MrpProduction, self).open_produce_product()
        action["context"] = {
            **literal_eval(action["context"]),
            **dict(stock_picking_type_code=self.picking_type_id.code),
        }
        return action
