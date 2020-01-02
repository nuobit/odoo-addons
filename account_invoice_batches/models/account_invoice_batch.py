# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from ast import literal_eval


class AccountInvoiceBatch(models.Model):
    _name = 'account.invoice.batch'
    _order = 'date desc'

    date = fields.Datetime(string='Date', required=True)

    name = fields.Char(string='Description')

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 copy=False, default=lambda self: self.env['res.company']._company_default_get())

    # all invoices
    invoice_ids = fields.One2many(comodel_name='account.invoice',
                                  inverse_name='invoice_batch_id', string='Invoices')

    invoice_count = fields.Integer(compute='_compute_invoice_count', string='Invoices')

    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)

    # draft (non-validated) invoices
    draft_invoice_ids = fields.One2many(comodel_name='account.invoice',
                                        domain=[('state', '=', 'draft')],
                                        inverse_name='invoice_batch_id', string='Draft')

    draft_invoice_count = fields.Integer(compute='_compute_draft_invoice_count', string='Draft')

    def _compute_draft_invoice_count(self):
        for rec in self:
            rec.draft_invoice_count = len(rec.draft_invoice_ids)

    # validated and unsent invoices
    unsent_invoice_ids = fields.One2many(comodel_name='account.invoice',
                                         domain=[('state', '!=', 'draft'),
                                                 ('sent', '=', False)],
                                         inverse_name='invoice_batch_id', string='Unsent')
    unsent_invoice_count = fields.Integer(compute='_compute_unsent_invoice_count',
                                          string='Unsent')

    def _compute_unsent_invoice_count(self):
        for rec in self:
            rec.unsent_invoice_count = len(rec.unsent_invoice_ids)

    # validated and sent invoices
    sent_invoice_ids = fields.One2many(comodel_name='account.invoice',
                                       domain=[('state', '!=', 'draft'),
                                               ('sent', '=', True)],
                                       inverse_name='invoice_batch_id', string='Sent')
    sent_invoice_count = fields.Integer(compute='_compute_sent_invoice_count', string='Sent')

    def _compute_sent_invoice_count(self):
        for rec in self:
            rec.sent_invoice_count = len(rec.sent_invoice_ids)

    @api.multi
    def name_get(self):
        lang = self.env['res.lang'].search([('code', '=', self.env.lang)])
        datetime_format = ' '.join(filter(None, map(lambda x: x and x.strip() or None,
                                                    [lang.date_format, lang.time_format])))
        res = []
        for rec in self:
            datetime_str = fields.Datetime.from_string(rec.date).strftime(datetime_format)
            value = filter(None, map(lambda x: x and x.strip() or None,
                                     [datetime_str, rec.name]))
            res.append((rec.id, ' '.join(value)))
        return res

    def account_invoice_batch_invoice_action(self, domain=[], context={}, name=None):
        self.ensure_one()
        action = self.env.ref('account_invoice_batches.account_invoice_batch_invoice_action').read()[0]

        if name:
            action['name'] = action['display_name'] = name

        domain += [
            ('invoice_batch_id', '=', self.id),
        ]
        domain_action = action['domain'] and action['domain'].replace('\n', '')
        domain_action = domain_action and literal_eval(domain_action) or []
        domain_action += domain
        action['domain'] = domain_action

        context.update({
            'search_default_invoice_batch_sending_method': True,
            'default_invoice_batch_id': self.id,
        })
        context_action = action['context'] and action['context'].replace('\n', '')
        context_action = context_action and literal_eval(context_action) or {}
        context_action.update(context)
        action['context'] = context_action

        return action

    def account_invoice_batch_all_invoice_action(self):
        return self.account_invoice_batch_invoice_action(
            name='All',
        )

    def account_invoice_batch_draft_invoice_action(self):
        return self.account_invoice_batch_invoice_action(
            domain=self.fields_get('draft_invoice_ids', 'domain')['draft_invoice_ids']['domain'],
            name='Draft',
        )

    def account_invoice_batch_unsent_invoice_action(self):
        return self.account_invoice_batch_invoice_action(
            domain=self.fields_get('unsent_invoice_ids', 'domain')['unsent_invoice_ids']['domain'],
            name='Unsent',
        )

    def account_invoice_batch_sent_invoice_action(self):
        return self.account_invoice_batch_invoice_action(
            domain=self.fields_get('sent_invoice_ids', 'domain')['sent_invoice_ids']['domain'],
            name='Sent',
        )
