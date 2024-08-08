# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResPartnerServiceReportConfig(models.Model):
    _name = "res.partner.service.report.config"
    _description = "Sale Order Report Xlsx Mapping Config"

    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company.id,
        string="Company",
        required=True,
        readonly=True,
    )
    name = fields.Char(string="Service Report Configuration Name", required=True)
    typology_ids = fields.One2many(
        comodel_name="res.partner.service.report.config.typology",
        inverse_name="config_id",
    )
    type_ids = fields.One2many(
        comodel_name="res.partner.service.report.config.type",
        inverse_name="config_id",
    )
