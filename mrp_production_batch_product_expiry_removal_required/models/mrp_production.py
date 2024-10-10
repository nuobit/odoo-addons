# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_produce_batch(self):
        return super(
            MrpProduction, self.with_context(skip_removal_date_check=True)
        ).action_produce_batch()
