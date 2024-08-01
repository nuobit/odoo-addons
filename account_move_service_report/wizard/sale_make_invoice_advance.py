# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def print_report_xlsx(self):
        sale_orders = self.env["sale.order"].browse(self._context.get("active_ids", []))
        iar = self.env["ir.actions.report"]
        report_name = "account_move_service_report.report_detailed_xlsx"
        return iar._get_report_from_name(report_name).report_action(sale_orders)
