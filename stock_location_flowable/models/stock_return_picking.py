# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import UserError


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _create_returns(self):
        self.ensure_one()
        move_line = self.picking_id.move_line_ids_without_package.filtered(
            lambda x: x.location_dest_id.flowable_storage
            and x.product_id in self.product_return_moves.product_id
        )
        if move_line:
            details = ", ".join(
                _("%s (%s)") % (ml.product_id.name, ml.location_dest_id.name)
                for ml in move_line
            )
            raise UserError(
                _(
                    "You cannot return the following products because"
                    " they come from a flowable location: %s"
                )
                % details
            )
        return super()._create_returns()
