import time

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

class TimesheetInvoiceFactor(models.Model):
    _name = 'timesheet.invoice.factor'
    _description = 'Invoice Rate'
    _order = 'factor'

    name = fields.Char('Internal Name', required=True, translate=True)
    customer_name = fields.Char('Name', help="Label for the customer")
    factor = fields.Float('Discount (%)', required=True, help="Discount in percentage", default=lambda *a: 0.0)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    invoice_id = fields.Many2one('account.invoice', 'Invoice', ondelete="set null", copy=False)
    to_invoice = fields.Many2one('timesheet.invoice.factor', 'Invoiceable', help="It allows to set the discount while making invoice, keep empty if the activities should not be invoiced.")


    def _get_invoice_price(self, account, product_id, user_id, qty):
        if account.pricelist_id:
            price = account.pricelist_id.price_get(product_id, qty or 1.0, account.partner_id.id)[account.pricelist_id.id]
        else:
            price = 0.0

        return price


    def _prepare_cost_invoice(self, partner, company_id, currency_id, analytic_lines):
        """ returns values used to create main invoice from analytic lines"""
        account_payment_term_obj = self.env['account.payment.term']
        invoice_name = analytic_lines[0].account_id.name

        date_due = False
        if partner.property_payment_term_id:
            pterm_list = partner.property_payment_term_id.compute(1, date_ref=time.strftime('%Y-%m-%d'))
            if pterm_list:
                pterm_list = [line[0] for line in pterm_list]
                pterm_list.sort()
                date_due = pterm_list[-1]

        return {
            'name': "%s - %s" % (time.strftime('%d/%m/%Y'), invoice_name),
            'partner_id': partner.id,
            'company_id': company_id,
            'payment_term': partner.property_payment_term_id.id or False,
            'account_id': partner.property_account_receivable_id.id,
            'currency_id': currency_id,
            'date_due': date_due,
            'fiscal_position': partner.property_account_position_id.id
        }

    def _prepare_cost_invoice_line(self, invoice_id, product_id, uom, user_id,
                                   factor_id, account, analytic_lines, data):
        product_obj = self.env['product.product']

        total_price = sum(l.amount for l in analytic_lines)
        total_qty = sum(l.unit_amount for l in analytic_lines)

        if data.product:
            # force product, use its public price
            unit_price = self.with_context(uom=uom)._get_invoice_price(account, data.product.id, user_id, total_qty)
        #elif journal_type == 'general' and product_id:
            # timesheets, use sale price
        #    unit_price = self.with_context(uom=uom)._get_invoice_price(account, data.product.id, user_id, total_qty)
        else:
            # expenses, using price from amount field
            unit_price = total_price * -1.0 / total_qty

        factor = self.env['timesheet.invoice.factor'].with_context(uom=uom).browse(factor_id)
        factor_name = factor.customer_name or ''
        curr_invoice_line = {
            'price_unit': unit_price,
            'quantity': total_qty,
            'product_id': product_id,
            'discount': factor.factor,
            'invoice_id': invoice_id,
            'name': factor_name,
            'uos_id': uom,
            'account_analytic_id': account.id,
        }

        if product_id:
            product = product_obj.with_context(uom=uom).browse(product_id)
            factor_name = product.name_get()[0][1]
            if factor.customer_name:
                factor_name += ' - ' + factor.customer_name

            general_account = product.property_account_income_id or product.categ_id.property_account_income_categ_id
            if not general_account:
                raise UserError(_("Configuration Error!") + '\n' + _(
                    "Please define income account for product '%s'.") % product.name)

            taxes = product.taxes_id or general_account.tax_ids
            tax = account.partner_id.property_account_position_id.map_tax(taxes)
            curr_invoice_line.update({
                'invoice_line_tax_id': [(6, 0, tax)],
                'name': factor_name,
                #'invoice_line_tax_id': [(6, 0, tax)],
                'account_id': general_account.id,
            })

            note = []
            for line in analytic_lines:
                # set invoice_line_note
                details = []
                if data.date:
                    details.append(line.date)
                if data.time:
                    if line.product_uom_id:
                        details.append("%s %s" % (line.unit_amount, line.product_uom_id.name))
                    else:
                        details.append("%s" % (line.unit_amount,))
                if data.name:
                    details.append(line.name)
                if details:
                    note.append(u' - '.join(map(lambda x: unicode(x) or '', details)))
            if note:
                curr_invoice_line['name'] += "\n" + ("\n".join(map(lambda x: unicode(x) or '', note)))

        return curr_invoice_line


    def invoice_cost_create(self, data=None):
        invoices = self.env['account.invoice']
        invoice_line_obj = self.env['account.invoice.line']
        analytic_line_obj = self.env['account.analytic.line']

        # use key (partner/account, company, currency)
        # creates one invoice per key
        invoice_grouping = {}

        currency_id = False
        # prepare for iteration on journal and accounts
        for line in self:
            key = (line.account_id.id,
                   line.account_id.company_id.id,
                   line.account_id.pricelist_id.currency_id.id)
            invoice_grouping.setdefault(key, []).append(line)

        for (key_id, company_id, currency_id), analytic_lines in invoice_grouping.items():
            # key_id is an account.analytic.account
            account = analytic_lines[0].account_id
            partner = account.partner_id  # will be the same for every line
            if (not partner) or not (currency_id):
                raise UserError(_('Contract incomplete. Please fill in the Customer and Pricelist fields for %s.') % (
                                         account.name,))

            curr_invoice = self._prepare_cost_invoice(partner, company_id, currency_id, analytic_lines)

            invoice_context = dict(lang=partner.lang,
                                   force_company=company_id,
                                   # set force_company in context so the correct product properties are selected (eg. income account)
                                   company_id=company_id)  # set company_id in context, so the correct default journal will be selected

            last_invoice = invoices.with_context(invoice_context).create(curr_invoice)

            # use key (product, uom, user, invoiceable, analytic account, journal type)
            # creates one invoice line per key
            invoice_lines_grouping = {}
            for analytic_line in analytic_lines:
                account = analytic_line.account_id

                if not analytic_line.to_invoice:
                    raise UserError(_('Trying to invoice non invoiceable line for %s.') % (
                        analytic_line.product_id.name))

                key = (analytic_line.product_id.id,
                       analytic_line.product_uom_id.id,
                       analytic_line.user_id.id,
                       analytic_line.to_invoice.id,
                       analytic_line.account_id,
                       #analytic_line.journal_id.type   #TODO usar is_:timesheet o alguna ltre x dif el timesheet de les lnes de factura
                       )
                # We want to retrieve the data in the partner language for the invoice creation
                analytic_line = analytic_line.with_context(invoice_context)

                invoice_lines_grouping.setdefault(key, []).append(analytic_line)

            # finally creates the invoice line
            for (product_id, uom, user_id, factor_id,
                 account), lines_to_invoice in invoice_lines_grouping.items():
                curr_invoice_line = self.with_context(invoice_context)._prepare_cost_invoice_line(last_invoice.id,
                                                                    product_id, uom, user_id, factor_id, account,
                                                                    lines_to_invoice,
                                                                    #journal_type
                                                                    data)
                invoice_line_obj.create(curr_invoice_line)

            analytic_line_obj.browse(map(lambda x: x.id, analytic_lines)).write({'invoice_id': last_invoice.id})
            #self.write(cr, uid, [l.id for l in analytic_lines], {'invoice_id': last_invoice}, context=context)
            #invoice_obj.button_reset_taxes(cr, uid, [last_invoice], context)
            invoices |= last_invoice

        return invoices

class TimesheetInvoiceCreate(models.TransientModel):
    _name = 'timesheet.invoice.create'
    _description = 'Create invoice from timesheet'

    date = fields.Boolean('Date', help='The real date of each work will be displayed on the invoice')
    time = fields.Boolean('Time spent', help='The time of each work done will be displayed on the invoice')
    name = fields.Boolean('Description', help='The detail of each work done will be displayed on the invoice')
    price = fields.Boolean('Cost', help='The cost of each work done will be displayed on the invoice. You probably don\'t want to check this')
    product = fields.Many2one('product.product', 'Force Product', help='Fill this field only if you want to force to use a specific product. Keep empty to use the real product that comes from the cost.')


    def view_init(self, fields):
        """
        This function checks for precondition before wizard executes
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user's ID for security checks,
        @param fields: List of fields for default value
        @param context: A standard dictionary for contextual values
        """
        analytic_obj = self.env['account.analytic.line']
        data = self.env.context and self.env.context.get('active_ids', [])
        for analytic in analytic_obj.browse(data):
            if analytic.invoice_id:
                raise UserError(_("Invoice is already linked to some of the analytic line(s)!"))


    def do_create(self):
        invoices = self.env['account.analytic.line'].browse(self._context.get('active_ids', [])).invoice_cost_create(data=self)

        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action
