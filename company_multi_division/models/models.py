# encoding: utf-8
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, fields


class Division(models.Model):
    _name = 'division.division'

    company_id = fields.Many2one('res.company', required=True)

    partner_id = fields.Many2one('res.partner', string='Division Partner', required=True)

    sale_order_sequence_id = fields.Many2one(
        'ir.sequence',
        string='Sale Order Sequence',
        domain="[('code', '=', 'sale.order')]",
    )  # , required=True)
    sale_order_report_id = fields.Many2one(
        'ir.actions.report.xml',
        string='Sale Order report Template',
        domain="[('model', '=', 'sale.order')]",
    )

    sale_invoice_journal_id = fields.Many2one(
        'account.journal',
        string='Sale Invoice Journal',
        domain="[('type', '=', 'sale')]",
    )
    sale_refund_invoice_journal_id = fields.Many2one(
        'account.journal',
        string='Sale Invoice refund Journal',
        domain="[('type', '=', 'sale_refund')]",
    )
    sale_invoice_report_id = fields.Many2one(
        'ir.actions.report.xml',
        string='Sale Invoice report Template',
        domain="[('model', '=', 'account.invoice')]",
    )

    sale_order_default = fields.Boolean('Default on sale orders', default=False)
    sale_invoice_default = fields.Boolean('Default on sale invoices', default=False)

    @api.multi
    def name_get(selfs):
        return [(self.id, self.partner_id.name) for self in selfs]


class ResCompanyDivision(models.Model):
    _inherit = 'res.company'

    division_ids = fields.One2many('division.division', inverse_name='company_id', string="Division")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    division_id = fields.Many2one('division.division', string="Division")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    division_id = fields.Many2one('division.division', string="Division")

    @api.multi
    def onchange_partner_id(self, part):
        res = super(SaleOrder, self).onchange_partner_id(part)

        division_id = False
        if part:
            partner_id = self.env['res.partner'].browse(part)
            if partner_id.parent_id:
                partner_id = partner_id.parent_id
            division_id = partner_id.division_id

        if not division_id:
            division_id = self.env.user.company_id.division_ids.filtered(lambda x: x.sale_order_default)
            if division_id:
                division_id = division_id[0]

        res['value'].update({'division_id': division_id.id })

        return res

    @api.multi
    def print_quotation(self):
        res = super(SaleOrder, self).print_quotation()

        if self.division_id and self.division_id.sale_order_report_id:
            return self.env['report'].get_action(self, self.division_id.sale_order_report_id.report_name)

        return res

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            division_id = vals.get('division_id')
            if division_id:
                division_obj = self.env['division.division'].browse(division_id)
                sequence_obj = division_obj.sale_order_sequence_id
                if sequence_obj:
                    vals['name'] = self.env['ir.sequence'].next_by_id(sequence_obj.id) or '/'

        new_id = super(SaleOrder, self).create(vals)

        return new_id

    @api.multi
    def _prepare_invoice(self, order, lines):
        invoice_vals = super(SaleOrder, self)._prepare_invoice(order, lines)

        if order.division_id:
            invoice_vals['division_id'] = order.division_id.id

        return invoice_vals




class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    division_id = fields.Many2one('division.division', string="Division")

    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False, company_id=False):

        res = super(AccountInvoice, self).onchange_partner_id(type, partner_id, date_invoice,
                            payment_term, partner_bank_id, company_id)

        if type in ('out_invoice', 'out_refund'):
            division_id = False
            if partner_id:
                partner_obj = self.env['res.partner'].browse(partner_id)
                if partner_obj.parent_id:
                    partner_obj = partner_obj.parent_id
                division_id = partner_obj.division_id

            if not division_id:
                division_id = self.env.user.company_id.division_ids.filtered(lambda x: x.sale_invoice_default)
                if division_id:
                    division_id = division_id[0]

            res['value'].update({'division_id': division_id.id})

        return res

    @api.onchange('division_id')
    def division_change(self):
        if self.division_id:
            if self.type == 'out_invoice':
                self.journal_id=self.division_id.sale_invoice_journal_id
            if self.type == 'out_refund':
                self.journal_id = self.division_id.sale_refund_invoice_journal_id

    @api.multi
    def onchange_company_id(self, company_id, part_id, type, invoice_line, currency_id):
        res = super(AccountInvoice, self).onchange_company_id(company_id, part_id, type, invoice_line, currency_id)

        """
        if type in ('out_invoice', 'out_refund'):
            division_id = False
            if part_id:
                partner_obj = self.env['res.partner'].browse(part_id)
                if partner_obj.parent_id:
                    partner_obj = partner_obj.parent_id
                division_id = partner_obj.division_id

            if not division_id:
                division_id = self.env.user.company_id.division_ids.filtered(lambda x: x.sale_invoice_default)
                if division_id:
                    division_id = division_id[0]

            if division_id and 'journal_id' in res['value']:
                del res['value']['journal_id']

            res['value'].update({'division_id': division_id.id})
        """

        if 'journal_id' in res['value']:
            del res['value']['journal_id']

        return res


    @api.multi
    def invoice_print(self):
        res = super(AccountInvoice, self).invoice_print()

        if self.division_id:
            action_name = self.division_id.sale_invoice_report_id.report_name
            return self.env['report'].get_action(self, action_name)

        return res

