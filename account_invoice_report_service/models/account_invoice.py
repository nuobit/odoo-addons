# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import re


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def print_report_invoice_service(self):
        if not self.company_id.report_service_id:
            raise UserError(_("There's no report defined on invoice company"))
        return self.company_id.report_service_id.report_action(self)

    def _group_by_order(self):
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

        return order_d, no_order

    def get_service_lines_by_order(self):
        # group by order
        order_d, no_order = self._group_by_order()

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

    def get_delivery_lines_by_order(self):
        # group by order
        order_d, no_order = self._group_by_order()

        # sort and join with lines w/o orders
        order_sorted_l = []
        for order, invoice_lines in sorted(order_d.items(),
                                           key=lambda x: (x[0].date_order,
                                                          x[0].client_order_ref,
                                                          x[0].service_number)):
            order_sorted_l.append((order, order_d[order].sorted(lambda x: (x.sequence, x.id))))

        if no_order:
            order_sorted_l.append((None, no_order.sorted(lambda x: (x.sequence, x.id))))

        return order_sorted_l


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def get_line_lots(self):
        return self.move_line_ids.mapped('move_line_ids.lot_id') \
            .sorted(lambda x: x.name).mapped('name')

    def _extract_product_code(self, name):
        m = re.match(r'^ *\[([^]]+)\] *(.*)$', name, flags=re.DOTALL)
        if not m:
            return None, name

        return m.groups()

    def get_splited_line_description(self):
        if not self.product_id:
            return None, self.name

        # find product data
        part = self.invoice_id.partner_id
        if part.lang:
            product = self.product_id.with_context(lang=part.lang)
        else:
            product = self.product_id

        product_partner_ref, product_name = self._extract_product_code(product.partner_ref)

        # find invoice line data
        line_partner_ref, line_name = self._extract_product_code(self.name)
        if line_partner_ref and line_partner_ref == product_partner_ref:
            return line_partner_ref, line_name

        return product_partner_ref, self.name
