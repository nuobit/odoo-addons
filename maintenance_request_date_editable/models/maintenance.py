# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    request_date_editable = fields.Boolean(compute="_compute_request_date_editable")

    @api.depends("stage_id", "company_id.maintenance_request_date_editable")
    def _compute_request_date_editable(self):
        for rec in self:
            rec.request_date_editable = (
                rec.company_id.maintenance_request_date_editable
                and not rec.stage_id.done
            )
