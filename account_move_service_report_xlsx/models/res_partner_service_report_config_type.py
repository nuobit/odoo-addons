# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartnerServiceReportConfigType(models.Model):
    _name = "res.partner.service.report.config.type"
    _description = "Res Partner Service Report Config Type"

    config_id = fields.Many2one(
        comodel_name="res.partner.service.report.config",
        ondelete="cascade",
        required=True,
    )
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
        relation="res_partner_service_report_config_type_product_rel",
        column1="type_id",
        column2="product_id",
        required=True,
    )

    @api.constrains("product_ids")
    def _check_product_ids(self):
        for rec in self:
            duplicate = rec.config_id.type_ids.filtered(
                lambda x: x.id != rec.id and bool(x.product_ids & rec.product_ids)
            )
            if duplicate:
                product_names = ", ".join(duplicate.mapped("product_ids.name"))
                raise ValidationError(
                    _(
                        "The following products are duplicated in the same configuration: %s"
                    )
                    % product_names
                )
