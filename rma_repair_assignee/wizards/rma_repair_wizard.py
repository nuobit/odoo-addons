# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class RmaRepairWizard(models.TransientModel):
    _inherit = "rma.repair.wizard"

    def _prepare_repair_order(self, line, lot_id=None):
        vals = super()._prepare_repair_order(line, lot_id=lot_id)
        vals["user_assignee_id"] = self.rma_id.user_assignee_id.id
        return vals
