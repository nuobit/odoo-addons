from datetime import date, time

from odoo import _, models


class AbstractReportXslx(models.AbstractModel):
    _name = "report.account_move_service_report_xlsx.report_sale"
    _description = "Abstract XLSX Account Move Service Report"
    _inherit = "report.report_xlsx.abstract"

    def report_values(self):
        invoice = ["order_line", "invoice_lines", "move_id"]
        return {
            _("Provider name"): ["company_id", "name"],
            _("ID Number (8 digits)"): ["auth_number"],
            _("Service Type"): [lambda x: x.get_service_typology_name()],
            _("Service Date"): ["service_date", lambda x: x.date()],
            _("Service Time"): ["service_date", lambda x: x.time()],
            _("Insurance Name"): ["service_insurer_name"],
            _("Insurance Code"): ["service_insurer_code"],
            _("Origin"): ["origin"],
            _("Destination"): ["destination"],
            _("KM Quantity"): [lambda x: x.get_service_type_quantity("km")],
            _("€/KM"): [lambda x: x.get_service_type_weighted_average_price("km")],
            _("Total KM (€)"): [lambda x: x.get_service_type_amount_total("km")],
            _("DEPARTURE (€)"): [lambda x: x.get_service_return_price_subtotal(False)],
            _("RETURN (€)"): [lambda x: x.get_service_return_price_subtotal(True)],
            _("ADDITIONAL (concept)"): [lambda x: x.get_service_additional_concept()],
            _("ADDITIONAL (€)"): [lambda x: x.get_service_type_subtotal("additional")],
            _("WAITING TIME (€)"): [lambda x: x.get_service_type_subtotal("wait")],
            _("Total by ID (€)"): [lambda x: x.get_service_total_by("auth_number")],
            _("Total Insurance (€)"): [
                lambda x: x.get_service_total_by("service_insurer_code")
            ],
            _("Patient (name and surname)"): ["insured_name"],
            _("Invoice Date"): invoice + ["invoice_date"],
            _("Invoice Number"): invoice + ["name"],
            _("Total Invoice"): invoice + ["amount_untaxed"],
        }

    def _get_service_row_data(self, account_move, sale_order, headers):
        row_data = []
        for header in headers:
            action_name = self.report_values().get(header)
            value = sale_order
            for action in action_name:
                if isinstance(value, models.Model):
                    if value._name == "account.move":
                        value = value.filtered(lambda x: x.id == account_move.id)
                if isinstance(action, str):
                    value = value[action]
                else:
                    value = action(value)
            row_data.append(value)
        return row_data

    def generate_xlsx_report(self, workbook, data, account_moves):
        headers = self.report_values().keys()
        report_name = _("Sales Service")
        sheet = workbook.add_worksheet(report_name[:31])
        bold = workbook.add_format({"bold": True})

        sheet.write_row(0, 0, headers, bold)
        orders = account_moves.invoice_line_ids.sale_line_ids.order_id
        orders.check_consistency_service_report_values()
        for row_num, sale_order in enumerate(orders, start=1):
            row_data = self._get_service_row_data(account_moves, sale_order, headers)
            for col_num, cell_value in enumerate(row_data):
                if not cell_value:
                    sheet.write(row_num, col_num, None)
                elif isinstance(cell_value, date):
                    date_format = workbook.add_format({"num_format": "dd/mm/yyyy"})
                    sheet.write(row_num, col_num, cell_value, date_format)
                elif isinstance(cell_value, time):
                    time_format = workbook.add_format({"num_format": "hh:mm"})
                    sheet.write(row_num, col_num, cell_value, time_format)
                else:
                    sheet.write(row_num, col_num, cell_value)
