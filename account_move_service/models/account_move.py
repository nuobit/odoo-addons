# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def get_service_record_fields_agg(self):
        return {"sale_line_ids"}

    def get_service_number_fields_agg(self):
        return {"price_unit": "price_subtotal"}

    def get_service_other_fields_agg(self, item):
        return (
            item.keys()
            - self.get_service_number_fields_agg().keys()
            - self.get_service_record_fields_agg()
            - self.prepare_invoice_service_line(self.env["sale.order.line"]).keys()
        )

    def prepare_invoice_service_line(self, so_line):
        product = self.get_config_service_group_product()
        return {
            "name": so_line.order_id.policy_number,
            "product_id": product.id,
            "quantity": 1,
        }

    def get_service_consistent_fields(self):
        return {"tax_ids": _("Taxes")}

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
            so_line = line[2].get("sale_line_ids", False)
            if so_line:
                if not all(item[0] == 4 for item in so_line) or len(so_line) > 1:
                    raise ValidationError(
                        _(
                            "Functionality not supported for the creation of invoices for "
                            "service intermediaries. Please contact your system "
                            "administrator."
                        )
                    )
                order = True
        if not order:
            return False
        return True

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("move_type", False) != "out_invoice":
                continue
            pid = vals.get("partner_id", False)
            if pid and self.env["res.partner"].browse(pid).service_intermediary:
                move_ok = self.check_invoice_service_values(vals)
                if not move_ok:
                    continue
                agg_lines = {}
                for line in vals.get("invoice_line_ids"):
                    # Check values
                    line_ok = self.check_invoice_service_line_values(line[2])
                    if not line_ok:
                        agg_lines[len(agg_lines)] = line[2]
                        continue
                    so_line = self.env["sale.order.line"].browse(
                        line[2].get("sale_line_ids")[0][1]
                    )
                    if not so_line.order_id.policy_number:
                        agg_lines[len(agg_lines)] = line[2]
                        continue

                    # Prepare values
                    line_data = agg_lines.setdefault(so_line.order_id.policy_number, {})
                    if not line_data:
                        line_data.update(self.prepare_invoice_service_line(so_line))

                    for f_num, f_name in self.get_service_number_fields_agg().items():
                        line_data[f_num] = line_data.get(f_num, 0) + so_line[f_name]
                    for f_rec in self.get_service_record_fields_agg():
                        line_data.setdefault(f_rec, []).extend(line[2].get(f_rec, []))
                    for f_other in self.get_service_other_fields_agg(line[2]):
                        if f_other not in line_data:
                            line_data[f_other] = line[2].get(f_other)
                        else:
                            if line_data[f_other] != line[2].get(f_other):
                                line_data[f_other] = False
                    for f_cons, f_name in self.get_service_consistent_fields().items():
                        if line_data[f_cons] != line[2].get(f_cons):
                            raise ValidationError(
                                _(
                                    "The field '%s' must have the same value for all "
                                    "order lines" % f_name
                                )
                            )

                vals["invoice_line_ids"] = [
                    (0, 0, agg_line)
                    for agg_line in [item_data for item_data in agg_lines.values()]
                ]

        return super().create(vals_list)
