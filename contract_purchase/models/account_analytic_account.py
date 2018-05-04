# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
import json


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    type = fields.Selection(related='journal_id.type', store=True)

    @api.onchange('partner_id')
    def _onchange_contract_purchase_partner_id(self):
        types = []
        if self.partner_id.customer:
            types.append('sale')
        if self.partner_id.supplier:
            types.append('purchase')

        journal = self.env['account.journal'].search(
            [('type', 'in', types),
             ('company_id', '=', self.company_id.id)])

        if len(journal) == 1:
            self.journal_id = journal.id
        else:
            if self.partner_id.customer and self.partner_id.supplier:
                self.journal_id = False

        if self.partner_id.customer and self.journal_id.type == 'sale':
            self.pricelist_id = self.partner_id.property_product_pricelist.id

    @api.onchange('journal_id')
    def _onchange_contract_purchase_journal_id(self):
        res = {}
        if self.journal_id:
            if self.journal_id.type == 'sale':
                if self.partner_id.customer:
                    self.pricelist_id = self.partner_id.property_product_pricelist.id
                else:
                    self.partner_id = False
                res.update({'domain': {'pricelist_id': False}})
            elif self.journal_id.type == 'purchase':
                if not self.partner_id.supplier:
                    self.partner_id = False
                self.pricelist_id = False
                res.update({'domain': {'pricelist_id': [('id', '=', False)]}})
        else:
            self.pricelist_id = False
            res.update({'domain': {'pricelist_id': [('id', '=', False)]}})

        return res

    @api.multi
    def _prepare_invoice(self):
        self.ensure_one()
        if not self.partner_id:
            raise ValidationError(
                _("You must first select a Partner for Contract %s!") %
                self.name)
        journal = self.journal_id or self.env['account.journal'].search(
            [('type', 'in', ('sale', 'purchase')),
             ('company_id', '=', self.company_id.id)],
            limit=1)
        if not journal:
            raise ValidationError(
                _("Please define a sale or purchase journal for the company '%s'.") %
                (self.company_id.name or '',))
        currency = (
                self.pricelist_id.currency_id or
                self.partner_id.property_product_pricelist.currency_id or
                self.company_id.currency_id
        )
        invoice = self.env['account.invoice'].new({
            'reference': self.code,
            'type': 'out_invoice' if journal.type == 'sale' else 'in_invoice',
            'partner_id': self.partner_id.address_get(
                ['invoice'])['invoice'],
            'currency_id': currency.id,
            'journal_id': journal.id,
            'date_invoice': self.recurring_next_date,
            'origin': self.name,
            'company_id': self.company_id.id,
            'contract_id': self.id,
            'user_id': self.partner_id.user_id.id,
        })
        # Get other invoice values from partner onchange
        invoice._onchange_partner_id()

        return invoice._convert_to_write(invoice._cache)

