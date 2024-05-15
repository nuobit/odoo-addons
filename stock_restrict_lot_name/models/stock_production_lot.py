# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>


from odoo import _, models
from odoo.exceptions import AccessError


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"

    def write(self, vals):
        if "name" in vals:
            if not self.env.is_superuser() and not self.user_has_groups(
                "stock_restrict_lot_name.group_update_lot_name_field"
            ):
                raise AccessError(
                    _(
                        "You do not have the required permissions to modify the name "
                        "of this lot. Please ask access to administrator."
                    )
                )
        return super().write(vals)
