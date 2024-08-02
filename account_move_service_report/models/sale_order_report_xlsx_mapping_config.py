# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class SaleOrderReportXlsxMappingConfig(models.Model):
    _name = "sale.order.report.xlsx.mapping.config"
    _description = "Sale Order Report Xlsx Mapping Config"

    name = fields.Char(string="Mapping Configuration Name", required=True)
    service_typology_ids = fields.One2many(
        comodel_name="sale.order.report.xlsx.mapping.config.service.typology",
        inverse_name="config_id",
    )
    service_type_ids = fields.One2many(
        comodel_name="sale.order.report.xlsx.mapping.config.service.type",
        inverse_name="config_id",
    )
