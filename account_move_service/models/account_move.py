# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def get_config_service_group_product(self):
        product = self.env.company.service_group_product
        if not product:
            raise ValidationError(
                _(
                    "This partner is an intermediary service and the service grouping "
                    "product has not been configured. Please set the default product "
                    "for service billing in the settings."
                )
            )
        return product

    def get_service_consistent_fields(self):
        return {"tax_ids": _("Taxes")}

    def get_service_record_fields_agg(self):
        return {"sale_line_ids"}

    def get_service_avg_num_fields_agg(self):
        return {"price_unit": ("quantity", "qty_to_invoice")}

    def get_service_number_fields_agg(self):
        return {
            "quantity": "qty_to_invoice",
        }

    def get_static_invoice_service_line_values(self, so_line):
        product = self.get_config_service_group_product()
        return {
            "name": so_line.order_id.policy_number,
            "product_id": product.id,
        }

    def get_service_other_fields_agg(self, item):
        return (
            item.keys()
            - self.get_service_number_fields_agg().keys()
            - self.get_service_avg_num_fields_agg().keys()
            - self.get_service_record_fields_agg()
            - self.get_static_invoice_service_line_values(
                self.env["sale.order.line"]
            ).keys()
        )

    def check_invoice_service_line_values(self, line):
        so_line = line.get("sale_line_ids", False)
        if not so_line:
            return False
        if not all(item[0] == 4 for item in so_line) or len(so_line) > 1:
            raise ValidationError(
                _(
                    "Functionality not supported for the creation of invoices for "
                    "service intermediaries. Please contact your system "
                    "administrator."
                )
            )
        return True

    def check_invoice_service_values(self, vals):
        invoice_line_ids = vals.get("invoice_line_ids", False)
        if not invoice_line_ids:
            return False
        if not all(item[0] == 0 for item in invoice_line_ids):
            raise ValidationError(
                _(
                    "Functionality not supported for the creation of invoices for "
                    "service intermediaries. Please contact your system "
                    "administrator."
                )
            )
        order = False
        for line in invoice_line_ids:
            if self.check_invoice_service_line_values(line[2]):
                order = True
        if not order:
            return False
        return True

    def prepare_invoice_service_line(self, line, agg_lines):
        # Check values
        line_ok = self.check_invoice_service_line_values(line)
        if line_ok:
            so_line = self.env["sale.order.line"].browse(
                line.get("sale_line_ids")[0][1]
            )
            if not so_line.order_id.policy_number:
                agg_lines[len(agg_lines)] = line
                return
        else:
            agg_lines[len(agg_lines)] = line
            return

        # Prepare values
        line_data = agg_lines.setdefault(so_line.order_id.policy_number, {})
        if not line_data:
            line_data.update(self.get_static_invoice_service_line_values(so_line))

        for f_name, (f_var1, f_var2) in self.get_service_avg_num_fields_agg().items():
            line_data[f_name] = (
                line_data.get(f_name, 0) * line_data.get(f_var1, 0)
                + (so_line[f_name] * so_line[f_var2])
            ) / (line_data.get(f_var1, 0) + so_line[f_var2])
        for f_num, f_name in self.get_service_number_fields_agg().items():
            line_data[f_num] = line_data.get(f_num, 0) + so_line[f_name]
        for f_rec in self.get_service_record_fields_agg():
            line_data.setdefault(f_rec, []).extend(line.get(f_rec, []))
        for f_other in self.get_service_other_fields_agg(line):
            if f_other not in line_data:
                line_data[f_other] = line.get(f_other)
            else:
                if line_data[f_other] != line.get(f_other):
                    line_data[f_other] = False
        for f_cons, f_name in self.get_service_consistent_fields().items():
            if line_data[f_cons] != line.get(f_cons):
                raise ValidationError(
                    _(
                        "The field '%s' must have the same value for all "
                        "order lines" % f_name
                    )
                )

    def prepare_invoice_service(self, vals):
        agg_lines = {}

        move_ok = self.check_invoice_service_values(vals)
        if move_ok:
            for line in vals.get("invoice_line_ids"):
                self.prepare_invoice_service_line(line[2], agg_lines)

        return agg_lines

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("move_type", False) == "out_invoice":
                pid = vals.get("partner_id", False)
                if pid and self.env["res.partner"].browse(pid).service_intermediary:
                    agg_lines = self.prepare_invoice_service(vals)
                    vals["invoice_line_ids"] = [
                        (0, 0, agg_line)
                        for agg_line in [item_data for item_data in agg_lines.values()]
                    ]

        return super().create(vals_list)
