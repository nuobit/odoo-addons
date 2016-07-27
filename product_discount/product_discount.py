# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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

from openerp import SUPERUSER_ID
#from openerp.osv import fields, osv
from openerp.tools.translate import _

from openerp import models, fields, api, _
from openerp.exceptions import AccessError, Warning, ValidationError, except_orm


class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def product_id_change(self, pricelist_id, product_id, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):

        res = super(sale_order_line, self).product_id_change(pricelist_id, product_id, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag)

        if not product_id:
            return res

        product_obj = self.env['product.product'].browse(product_id)

        pricelist_obj = self.env['product.pricelist'].browse(pricelist_id)
        price_net, rule_id = pricelist_obj.price_rule_get(product_id, qty or 1.0, partner_id)[pricelist_id]

        rule_obj = self.env['product.pricelist.item'].browse(rule_id)
        if rule_obj.price_discount == -1.0 and rule_obj.price_surcharge!=0.0: # es un net
            price = rule_obj.price_surcharge
            if self.env.uid == SUPERUSER_ID and self.env.context.get('company_id'):
                taxes = product_obj.taxes_id.filtered(lambda r: r.company_id.id == self.env.context['company_id'])
            else:
                taxes = product_obj.taxes_id
            tax_obj = self.env['account.tax']
            price = tax_obj._fix_tax_included_price(price, taxes, res['value']['tax_id'])

            discount = 0.0
        else:
            price = product_obj.list_price
            discount = (1 - price_net / price) * 100

        res['value']['discount'] = discount
        res['value']['price_unit'] = price


        return res


#TODO: discounts on invoices
'''
class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
            company_id=None):


        res = super(account_invoice_line, self).product_id_change(pricelist_id, product_id, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag)


        context = self._context
        company_id = company_id if company_id is not None else context.get('company_id', False)
        self = self.with_context(company_id=company_id, force_company=company_id)

        if not partner_id:
            raise except_orm(_('No Partner Defined!'), _("You must first select a partner!"))
        if not product:
            if type in ('in_invoice', 'in_refund'):
                return {'value': {}, 'domain': {'uos_id': []}}
            else:
                return {'value': {'price_unit': 0.0}, 'domain': {'uos_id': []}}

        values = {}

        part = self.env['res.partner'].browse(partner_id)
        fpos = self.env['account.fiscal.position'].browse(fposition_id)

        if part.lang:
            self = self.with_context(lang=part.lang)
        product = self.env['product.product'].browse(product)

        values['name'] = product.partner_ref
        if type in ('out_invoice', 'out_refund'):
            account = product.property_account_income or product.categ_id.property_account_income_categ
        else:
            account = product.property_account_expense or product.categ_id.property_account_expense_categ
        account = fpos.map_account(account)
        if account:
            values['account_id'] = account.id

        if type in ('out_invoice', 'out_refund'):
            taxes = product.taxes_id or account.tax_ids
            if product.description_sale:
                values['name'] += '\n' + product.description_sale
        else:
            taxes = product.supplier_taxes_id or account.tax_ids
            if product.description_purchase:
                values['name'] += '\n' + product.description_purchase

        fp_taxes = fpos.map_tax(taxes)
        values['invoice_line_tax_id'] = fp_taxes.ids

        if type in ('in_invoice', 'in_refund'):
            if price_unit and price_unit != product.standard_price:
                values['price_unit'] = price_unit
            else:
                values['price_unit'] = self.env['account.tax']._fix_tax_included_price(product.standard_price, taxes, fp_taxes.ids)
        else:
            values['price_unit'] = self.env['account.tax']._fix_tax_included_price(product.lst_price, taxes, fp_taxes.ids)

        values['uos_id'] = product.uom_id.id
        if uom_id:
            uom = self.env['product.uom'].browse(uom_id)
            if product.uom_id.category_id.id == uom.category_id.id:
                values['uos_id'] = uom_id

        domain = {'uos_id': [('category_id', '=', product.uom_id.category_id.id)]}

        company = self.env['res.company'].browse(company_id)
        currency = self.env['res.currency'].browse(currency_id)

        if company and currency:
            if company.currency_id != currency:
                values['price_unit'] = values['price_unit'] * currency.rate

            if values['uos_id'] and values['uos_id'] != product.uom_id.id:
                values['price_unit'] = self.env['product.uom']._compute_price(
                    product.uom_id.id, values['price_unit'], values['uos_id'])

        return {'value': values, 'domain': domain}
'''