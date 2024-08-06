# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    service_report_config_id = fields.Many2one(
        string="Service Report Configuration",
        comodel_name="res.partner.service.report.config",
        help="Intermediary mapping for service billing",
    )
