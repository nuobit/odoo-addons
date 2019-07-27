# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def print_report_invoice_service(self):
        return self.env.ref('account_invoice_report_service.action_report_invoice_service').report_action(self)

    def get_lines_by_order(self):
        # grouping by order
        ilines_trace = self.env['account.invoice.line']
        order_d, no_order = {}, self.env['account.invoice.line']
        for iline in self.invoice_line_ids:
            if iline.sale_line_ids:
                for oline in iline.sale_line_ids:
                    if iline in ilines_trace:
                        raise Exception(_("Not implemented case: The same invoice line belongs to different orders"))
                    ilines_trace += iline
                    order = oline.order_id
                    if order not in order_d:
                        order_d[order] = self.env['account.invoice.line']
                    order_d[order] += iline
            else:
                no_order += iline

        # sorting
        order_sorted_l = []
        for order, ilines in sorted(order_d.items(), key=lambda x: (x[0].confirmation_date, x[0].service_number)):
            order_sorted_l.append((order, ilines.sorted(lambda x: (x.sequence, x.id))))

        if no_order:
            order_sorted_l.append((None, no_order.sorted(lambda x: (x.sequence, x.id))))

        return order_sorted_l
