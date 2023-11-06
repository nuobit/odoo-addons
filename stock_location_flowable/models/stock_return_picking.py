# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import UserError


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _create_returns(self):
        res = super()._create_returns()
        for rec in self:
            move_line = rec.picking_id.move_line_ids_without_package.filtered(
                lambda x: x.location_dest_id.flowable_storage
                and x.product_id in rec.product_return_moves.product_id
            )
            if move_line:
                raise UserError(
                    _(
                        "You cannot return the product %s because it"
                        " comes from a flowable location %s."
                    )
                    % (move_line.product_id.name, move_line.location_dest_id.name)
                )
        return res
