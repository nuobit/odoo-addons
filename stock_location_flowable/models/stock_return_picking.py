# Copyright NuoBiT Solutions SL - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL- Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import UserError


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _create_return(self):
        self.ensure_one()
        move_line = self.picking_id.move_line_ids_without_package.filtered(
            lambda x: x.location_dest_id.flowable_storage
            and x.product_id in self.product_return_moves.product_id
        )
        if move_line:
            detail_tpl = _("%(product)s (%(location)s)")
            details = ", ".join(
                detail_tpl
                % {
                    "product": ml.product_id.name,
                    "location": ml.location_dest_id.name,
                }
                for ml in move_line
            )
            raise UserError(
                _(
                    "You cannot return the following products because"
                    " they come from a flowable location: %s"
                )
                % details
            )
        return super()._create_return()
