# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class RepairLine(models.Model):
    _inherit = "repair.line"

    @api.onchange("type")
    def onchange_operation_type(self):
        super().onchange_operation_type()
        if self.type == "add":
            self.location_id = self.repair_id.location_id
