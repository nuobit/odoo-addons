# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    partner_service_intermediary = fields.Boolean(
        related="partner_id.service_intermediary"
    )

    def check_consistency_service_report_values(self):
        for rec in self:
            if rec.state != "posted":
                raise ValidationError(
                    _(
                        "The invoice must be posted to generate "
                        "sales service spreadsheet."
                    )
                )
            if rec.partner_service_intermediary:
                if not rec.partner_id.service_report_config_id:
                    raise ValidationError(
                        _(
                            "The client %s does not have the service report settings "
                            "configured. Please go to the contact and set it up."
                        )
                        % rec.partner_id.name
                    )
                allowed_products = (
                    rec.partner_id.service_report_config_id.type_ids.mapped(
                        "product_ids"
                    )
                )
                invoice_products = rec.invoice_line_ids.sale_line_ids.mapped(
                    "product_id"
                )
                wrong_products = invoice_products.filtered(
                    lambda p: p not in allowed_products
                )
                if wrong_products:
                    inconsistent_product_names = "\n-".join(
                        wrong_products.mapped("name")
                    )
                    raise ValidationError(
                        _(
                            "In the sale orders linked to this invoice, there are "
                            "products that are not included in the allowed service "
                            "types for this service intermediary: \n-%s\nPlease go to "
                            "the service report configuration and add the missing "
                            "products."
                        )
                        % inconsistent_product_names
                    )
            else:
                raise ValidationError(
                    _(
                        "The partner is not a service intermediary and cannot "
                        "generate the sales service spreadsheet."
                    )
                )

    def print_report_sale_service_spreadsheet(self):
        self.ensure_one()
        self.check_consistency_service_report_values()
        return {
            "type": "ir.actions.report",
            "report_name": "account_move_service_report_xlsx.report_sale",
            "report_type": "xlsx",
            "context": dict(
                self.env.context, active_ids=self.ids, sale_service_report=True
            ),
        }
