# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class Picking(models.Model):
    _inherit = "stock.picking"

    def action_assign(self):
        if not self.env.context.get("skip_reserved_quantity", False):
            super().action_assign()
