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
            _("ADDITIONAL (€)"): [lambda x: x.get_service_type_price_subtotal("additional")],
            _("WAITING TIME (€)"): [lambda x: x.get_service_type_price_subtotal("wait")],
            _("Total by ID (€)"): ["total_by_id"],  # TODO: function
            _("Total Insurance (€)"): ["total_insurance"],  # TODO: function
            _("Patient (name and surname)"): ["insured_name"],
            _("Invoice Date"): ["service_invoice_creation_date"],
            _("Invoice Number"): ["service_invoice_number"],
            _("Total Invoice"): ["amount_total"],
        }

    def generate_xlsx_report(self, workbook, data, account_moves):
        headers = self.report_values().keys()
        report_name = _("Detailed Invoice Service")
        sheet = workbook.add_worksheet(report_name[:31])
        bold = workbook.add_format({"bold": True})

        sheet.write_row(0, 0, headers, bold)
        if account_moves.partner_id.service_intermediary:
            for row_num, sale_order in enumerate(account_moves.invoice_line_ids.sale_line_ids.order_id, start=1):
                row_data = []
                for header in headers:
                    action_name = self.report_values().get(header)
                    value = sale_order
                    for action in action_name:
                        if isinstance(action, str):
                            value = value[action]
                        else:
                            value = action(value)
                    row_data.append(str(value))
                sheet.write_row(row_num, 0, row_data)


        # for row_num, sale_order in enumerate(account_moves, start=1):
        #     row_data = []
        #     for header in headers:
        #         field_name = self.report_values().get(header)
        #         value = sale_order
        #         if isinstance(field_name, list):
        #             for field in field_name:
        #                 value = getattr(value, field, "")
        #         elif isinstance(field_name, tuple):
        #             for function in field_name:
        #                 value = getattr(value, function, "")()
        #         row_data.append(str(value))
        #     sheet.write_row(row_num, 0, row_data)
