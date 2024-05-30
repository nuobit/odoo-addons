# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class RmaRepairWizard(models.TransientModel):
    _inherit = "rma.repair.wizard"

    def _prepare_repair_order(self, lot_id=None):
        vals = super()._prepare_repair_order(lot_id=lot_id)
        vals["employee_id"] = self.rma_id.employee_id.id
        return vals
