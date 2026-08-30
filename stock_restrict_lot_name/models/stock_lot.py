# Copyright NuoBiT Solutions- Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import AccessError


class StockLot(models.Model):
    _inherit = "stock.lot"

    def write(self, vals):
        if "name" in vals:
            if not self.env.is_superuser() and not self.env.user.has_group(
                "stock_restrict_lot_name.group_update_lot_name_field"
            ):
                raise AccessError(
                    _(
                        "You do not have the required permissions to modify the name "
                        "of this lot. Please ask access to administrator."
                    )
                )
        return super().write(vals)
