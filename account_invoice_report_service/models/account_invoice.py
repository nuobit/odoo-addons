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
                        raise ValidationError(
                            _("Not implemented case: The same invoice line belongs to different orders"))
                    ilines_trace |= iline
                    order = oline.order_id
                    if order not in order_d:
                        order_d[order] = self.env['account.invoice.line']
                    order_d[order] |= iline
            else:
                no_order += iline

        # grouping by round trip code
        order_rt_date_l = []
        order_rt_d = {}
        for order in order_d:
            rt_code = order.round_trip_code
            if rt_code:
                if rt_code not in order_rt_d:
                    order_rt_d[rt_code] = self.env['sale.order']
                order_rt_d[rt_code] |= order
            else:
                order_rt_date_l.append((order, order))

        # sort round trip classified orders by return_service
        for dummy, orders in order_rt_d.items():
            going_order = orders.filtered(lambda x: not x.return_service)
            if going_order:
                going_order = going_order[0]
            else:
                going_order = orders.sorted(lambda x: x.service_date)[0]

            for o in orders:
                order_rt_date_l.append((going_order, o))

        # sort and join with lines w/o orders
        order_sorted_l = []
        for dummy, order in sorted(order_rt_date_l, key=lambda x: (x[0].service_date, x[0].service_number,
                                                                   x[1].round_trip_code, x[1].return_service,
                                                                   x[1].service_number)):
            order_sorted_l.append((order, order_d[order].sorted(lambda x: (x.sequence, x.id))))

        if no_order:
            order_sorted_l.append((None, no_order.sorted(lambda x: (x.sequence, x.id))))

        return order_sorted_l
