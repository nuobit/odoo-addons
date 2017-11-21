import time

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

import odoo.addons.decimal_precision as dp

class TimesheetInvoiceFactor(models.Model):
    _name = 'timesheet.invoice.factor'
    _description = 'Invoice Rate'
    _order = 'factor'

    name = fields.Char('Internal Name', required=True, translate=True)
    customer_name = fields.Char('Name', help="Label for the customer")
    factor = fields.Float('Discount (%)', required=True, help="Discount in percentage", default=lambda *a: 0.0)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    product_id = fields.Many2one('product.product', 'Product',
                                      help="If you want to reinvoice working time of employees, link this employee to a service to determinate the cost price of the job.")




class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    invoice_on_timesheets = fields.Boolean("On Timesheets")
    hours_qtt_est = fields.Float('Estimation of Hours to Invoice')
    timesheet_ca_invoiced = fields.Float(compute='_timesheet_ca_invoiced_calc', string='Remaining Time',
                                             help="Sum of timesheet lines invoiced for this contract.")
    remaining_hours_to_invoice = fields.Float(compute='_remaining_hours_to_invoice_calc',
                                                  string='Remaining Time',
                                                  help="Computed using the formula: Expected on timesheets - Total invoiced on timesheets")
    ca_to_invoice = fields.Float(compute='_ca_to_invoice_calc', string='Uninvoiced Amount',
                                     help="If invoice from analytic account, the remaining amount you can invoice to the customer based on the total costs.",
                                     digits=dp.get_precision('Account'))


    ##################

    to_invoice = fields.Many2one('timesheet.invoice.factor', 'Timesheet Invoicing Ratio',
                                  help="You usually invoice 100% of the timesheets. But if you mix fixed price and timesheet invoicing, you may use another ratio. For instance, if you do a 20% advance invoice (fixed price, based on a sales order), you should invoice the rest on timesheet with a 80% ratio.")


    ###########
    @api.onchange('invoice_on_timesheets')
    def timesheet_invoice_check_invoice_on_timesheets(self):
        if not self.invoice_on_timesheets:
            return {'value': {'to_invoice': False}}

        try:
            #to_invoice = self.env['ir.model.data'].get_object_reference('timesheet_invoice', 'timesheet_invoice_factor1')
            to_invoice = self.env.ref('timesheet_invoice.timesheet_invoice_factor1')
            return {'value': {'to_invoice': to_invoice}}
        except ValueError:
            pass



    def _timesheet_ca_invoiced_calc(self):
        pass
        '''
        lines_obj = self.pool.get('account.analytic.line')
        res = {}
        inv_ids = []
        for account in self.browse(cr, uid, ids, context=context):
            res[account.id] = 0.0
            line_ids = lines_obj.search(cr, uid, [('account_id','=', account.id), ('invoice_id','!=',False), ('invoice_id.state', 'not in', ['draft', 'cancel']), ('to_invoice','!=', False), ('journal_id.type', '=', 'general'), ('invoice_id.type', 'in', ['out_invoice', 'out_refund'])], context=context)
            for line in lines_obj.browse(cr, uid, line_ids, context=context):
                if line.invoice_id not in inv_ids:
                    inv_ids.append(line.invoice_id)
                    if line.invoice_id.type == 'out_refund':
                        res[account.id] -= line.invoice_id.amount_untaxed
                    else:
                        res[account.id] += line.invoice_id.amount_untaxed
        return res
        '''

    def _remaining_hours_to_invoice_calc(selfg):
        pass
        '''

        res = {}
        for account in self.browse(cr, uid, ids, context=context):
            res[account.id] = max(account.hours_qtt_est - account.timesheet_ca_invoiced, account.ca_to_invoice)
        return res
        '''

    def _ca_to_invoice_calc(selfs):
        for self in selfs:
            self.ca_to_invoice = 0.0

            invoice_grouping = {}
            lines = self.line_ids.filtered(lambda x: x.project_id and not x.invoice_id and x.to_invoice)
            for line in lines:
                key = (line.product_id.id,
                       line.user_id.id,
                       line.to_invoice.id,
                       line.product_uom_id.id,
                       line.name)

                if key not in invoice_grouping:
                    invoice_grouping[key] = dict(amount=0.0, qty=0.0)
                invoice_grouping[key]['amount'] += line.amount
                invoice_grouping[key]['qty'] += line.unit_amount

            for (product_id, user_id, factor_id, uom, line_name), amounts in invoice_grouping.items():
                price, qty = amounts['amount'], amounts['qty']

                price = -price
                if product_id:
                    price = self.env['account.analytic.line']._get_invoice_price(self, product_id, user_id, qty)
                factor = self.env['timesheet.invoice.factor'].browse(factor_id)

                self.ca_to_invoice += price * qty * (100 - factor.factor or 0.0) / 100.0


    #############

    def to_invoice_timesheets(self):
        domain = [('invoice_id', '=', False), ('to_invoice', '!=', False), ('project_id', '!=' , False), #('journal_id.type', '=', 'general'),
                  ('account_id', '=', self.id)]
        name = _('Timesheets to Invoice of %s') % ','.join([record.name for record in self])
        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': domain,
            'res_model': 'account.analytic.line',
            'nodestroy': True,
        }



class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.model
    def _default_product(self):
        user_id = self.env.context.get('user_id', self.env.user.id)
        employee = self.env['hr.employee'].search([('user_id', '=', user_id)])

        return employee.product_id.id

    invoice_id = fields.Many2one('account.invoice', 'Invoice', ondelete="set null", copy=False)
    to_invoice = fields.Many2one('timesheet.invoice.factor', 'Invoiceable',
                                 help="It allows to set the discount while making invoice, keep empty if the activities should not be invoiced.")

    product_id = fields.Many2one(default=_default_product)

    @api.model
    def create(self, vals):
        if not vals.get('to_invoice') and vals.get('project_id'):
            project = self.env['project.project'].browse(vals.get('project_id'))
            vals['to_invoice'] = project.analytic_account_id.to_invoice.id
        return super(AccountAnalyticLine, self).create(vals)

    '''
    def write(self, cr, uid, ids, vals, context=None):
        self._check_inv(cr, uid, ids, vals)
        return super(account_analytic_line,self).write(cr, uid, ids, vals,
                context=context)

    def _check_inv(self, cr, uid, ids, vals):
        select = ids
        if isinstance(select, (int, long)):
            select = [ids]
        if ( not vals.has_key('invoice_id')) or vals['invoice_id' ] == False:
            for line in self.browse(cr, uid, select):
                if line.invoice_id:
                    raise osv.except_osv(_('Error!'),
                        _('You cannot modify an invoiced analytic line!'))
        return True
    '''


    ############
    def _get_invoice_price(self, account, product_id, user_id, qty):
        if account.pricelist_id:
            price = account.pricelist_id.price_get(product_id, qty or 1.0, account.partner_id.id)[account.pricelist_id.id]
        else:
            price = 0.0

        return price


    def _prepare_cost_invoice(self, partner, company_id, currency_id, analytic_lines):
        """ returns values used to create main invoice from analytic lines"""
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
            'payment_term_id': partner.property_payment_term_id.id or False,
            'account_id': partner.property_account_receivable_id.id,
            'currency_id': currency_id,
            'date_due': date_due,
            'fiscal_position_id': partner.property_account_position_id.id
        }

    def _prepare_cost_invoice_line(self, invoice_id, product_id, uom, user_id,
                                   factor_id, account, analytic_lines, data):
        total_qty = sum(l.unit_amount for l in analytic_lines)
        if data.product:
            # force product, use its public price
            unit_price = self.with_context(uom=uom)._get_invoice_price(account, data.product.id, user_id, total_qty)
        elif product_id:
            # timesheets, use sale price
            unit_price = self.with_context(uom=uom)._get_invoice_price(account, product_id, user_id, total_qty)
        else:
            raise UserError(_("There's a line without product."))

            #total_price = sum(l.amount for l in analytic_lines)
            # expenses, using price from amount field
            #unit_price = total_price * -1.0 / total_qty

        factor = self.env['timesheet.invoice.factor'].with_context(uom=uom).browse(factor_id)
        factor_name = factor.customer_name or ''
        curr_invoice_line = {
            'price_unit': unit_price,
            'quantity': total_qty,
            'product_id': product_id,
            'discount': factor.factor,
            'invoice_id': invoice_id,
            'name': factor_name,
            'uom_id': uom,
            'account_analytic_id': account.id,
        }

        if product_id:
            product = self.env['product.product'].with_context(uom=uom).browse(product_id)
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
                'invoice_line_tax_ids': [(6, 0, tax.mapped('id'))],
                'name': factor_name,
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
            last_invoice.compute_taxes()
            invoices |= last_invoice

        return invoices


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def create_analytic_lines(self):
        res = super(AccountMoveLine, self).create_analytic_lines()
        for obj_line in self:
            #For customer invoice, link analytic line to the invoice so it is not proposed for invoicing in Bill Tasks Work
            invoice_id = obj_line.invoice_id and obj_line.invoice_id.type in ('out_invoice','out_refund') and obj_line.invoice_id.id or False
            for line in obj_line.analytic_line_ids:
                line.write({
                    'invoice_id': invoice_id,
                    'to_invoice': line.account_id.to_invoice and line.account_id.to_invoice.id or False
                    })
        return res

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
