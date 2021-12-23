# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Christopher Ormaza <chris.ormaza@forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    report_service_id = fields.Many2one(
        related="company_id.report_service_id", readonly=False
    )
