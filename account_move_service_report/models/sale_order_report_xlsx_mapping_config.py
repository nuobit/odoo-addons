# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class SaleOrderReportXlsxMappingConfig(models.Model):
    _name = "sale.order.report.xlsx.mapping.config"
    _description = "Sale Order Report Xlsx Mapping Config"

    name = fields.Char(string="Mapping Configuration Name", required=True)
    field_mapping_name = fields.Char()
    field_mapping_string = fields.Char()
    service_typology_ids = fields.One2many(
        comodel_name="sale.order.report.xlsx.mapping.config.service.typology",
        inverse_name="config_id",
    )
    service_type_ids = fields.One2many(
        comodel_name="sale.order.report.xlsx.mapping.config.service.type",
        inverse_name="config_id",
    )


class SaleOrderReportXlsxMappingConfigServiceTypology(models.Model):
    _name = "sale.order.report.xlsx.mapping.config.service.typology"
    _description = "Sale Order Report Xlsx Mapping Config Service Typology"

    config_id = fields.Many2one(comodel_name="sale.order.report.xlsx.mapping.config")
    name = fields.Char()
    key = fields.Char()
    transfer_reason = fields.Char()


class SaleOrderReportXlsxMappingConfigServiceType(models.Model):
    _name = "sale.order.report.xlsx.mapping.config.service.type"
    _description = "Sale Order Report Xlsx Mapping Config Service Type"

    config_id = fields.Many2one(comodel_name="sale.order.report.xlsx.mapping.config")
    type = fields.Selection(
        selection=[
            ("service", "Service"),
            ("km", "Km"),
            ("additional", "Additional"),
            ("wait", "Wait"),
        ],
        required=True,
    )
    name = fields.Char(required=True)
    product_ids = fields.Many2many(
        comodel_name="product.product",
        relation="sale_order_report_xlsx_mapping_config_type_service_product_rel",
        column1="type_service_id",
        column2="product_id",
        required=True,
    )
