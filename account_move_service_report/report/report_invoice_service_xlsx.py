from odoo import _, models


class AbstractReportXslx(models.AbstractModel):
    _name = "report.account_move_service_report.report_detailed_xlsx"
    _description = "Abstract XLSX Account Move Service Report"
    _inherit = "report.report_xlsx.abstract"

    def report_values(self):
        return {
            _("Provider name"): ["company_id", "name"],
            _("ID Number (8 digits)"): ["auth_number"],
            _("Service Type"): [lambda x: x.get_service_typology_name()],
            _("Service Date"): ["service_date", lambda x: x.date()],
            _("Service Time"): ["service_date", lambda x: x.time()],
            _("Insurance Name"): ["service_name"],
            _("Insurance Code"): ["service_code"],
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
            _("Total Insurance (€)"): [lambda x: x.get_service_total_by("service_code")],
            _("Patient (name and surname)"): ["insured_name"],
            _("Invoice Date"): ["service_invoice_creation_date"],
            _("Invoice Number"): ["service_invoice_number"],
            _("Total Invoice"): ["order_line", "invoice_lines", "move_id", "amount_total"],
        }

    def _get_service_row_data(self, sale_order, headers):
        row_data = []
        for header in headers:
            action_name = self.report_values().get(header)
            value = sale_order
            for action in action_name:
                if isinstance(action, str):
                    value = value[action]
                else:
                    value = action(value)
            if value in [0, False, None]:
                value = ""
            if isinstance(value, (int, float)):
                row_data.append(value)
            else:
                row_data.append(str(value))
        return row_data

    def generate_xlsx_report(self, workbook, data, account_moves):
        headers = self.report_values().keys()
        report_name = _("Sales Service")
        sheet = workbook.add_worksheet(report_name[:31])
        bold = workbook.add_format({"bold": True})

        sheet.write_row(0, 0, headers, bold)
        if account_moves.partner_id.service_intermediary:
            orders = account_moves.invoice_line_ids.sale_line_ids.order_id
            for row_num, sale_order in enumerate(orders, start=1):
                row_data = self._get_service_row_data(sale_order, headers)
                sheet.write_row(row_num, 0, row_data)
