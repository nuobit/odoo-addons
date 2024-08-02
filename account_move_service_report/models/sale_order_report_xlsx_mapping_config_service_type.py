# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


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
    name = fields.Char()
    product_ids = fields.Many2many(
        comodel_name="product.product",
        relation="sale_order_report_xlsx_mapping_config_type_service_product_rel",
        column1="type_service_id",
        column2="product_id",
        required=True,
    )

    @api.constrains("product_ids")
    def _check_product_ids(self):
        for rec in self:
            duplicate = rec.config_id.service_type_ids.filtered(
                lambda x: x.id != rec.id and bool(x.product_ids & rec.product_ids)
            )
            if duplicate:
                product_names = ', '.join(duplicate.mapped('product_ids.name'))
                raise ValidationError(
                    _(
                        "The following products are duplicated in the same configuration: %s"
                    ) % product_names
                )
