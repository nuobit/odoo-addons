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

from itertools import chain
import time

from openerp import tools, SUPERUSER_ID
from openerp.osv import osv
from openerp.tools.translate import _

from openerp import models, fields, api, _
from openerp.exceptions import AccessError, Warning, ValidationError, except_orm
import openerp.addons.decimal_precision as dp


class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def product_id_change(self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):

        res = super(sale_order_line, self).product_id_change(pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag)

        if not product:
            return res

        product_obj = self.env['product.product'].browse(product)

        pricelist_obj = self.env['product.pricelist'].browse(pricelist)
        price_net, rule_ids = pricelist_obj.price_rule_get(product, qty or 1.0, partner_id)[pricelist]
        if not rule_ids:
            return res

        base_price, rule_id = rule_ids[0]
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
            price = base_price
            if price>0:
                discount = (1.0 - price_net / price) * 100.0
            else:
                discount = 0.0

        res['value']['discount'] = discount
        res['value']['price_unit'] = price

        return res


class purchase_order(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _prepare_inv_line(self, account_id, order_line):
        result = super(purchase_order, self)._prepare_inv_line(
            account_id, order_line)
        result['discount'] = order_line.discount or 0.0
        return result

    @api.model
    def _prepare_order_line_move(self, order, order_line, picking_id,
                                 group_id):
        res = super(purchase_order, self)._prepare_order_line_move(
            order, order_line, picking_id, group_id)
        for vals in res:
            vals['price_unit'] = (vals.get('price_unit', 0.0) *
                                  (1 - (order_line.discount / 100)))
        return res

class purchase_order_line(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _calc_line_base_price(self, line):
        res = super(purchase_order_line, self)._calc_line_base_price(line)
        return res * (1 - line.discount / 100.0)

    discount = fields.Float(
        string='Discount (%)', digits_compute=dp.get_precision('Discount'))

    _sql_constraints = [
        ('discount_limit', 'CHECK (discount <= 100.0)',
         'Discount must be lower than 100%.'),
    ]

    @api.multi
    def onchange_product_id(self, pricelist_id, product_id, qty, uom_id,
                        partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
                        name=False, price_unit=False, state='draft'):
        res = super(purchase_order_line, self).product_id_change(pricelist_id, product_id, qty, uom_id,
                                                                 partner_id, date_order, fiscal_position_id,
                                                                 date_planned, name, price_unit, state)

        if not product_id:
            return res

        product_obj = self.env['product.product'].browse(product_id)

        pricelist_obj = self.env['product.pricelist'].browse(pricelist_id)
        price_net, rule_ids = pricelist_obj.price_rule_get(product_id, qty or 1.0, partner_id)[pricelist_id]
        if not rule_ids:
            return res

        base_price, rule_id = rule_ids[0]
        rule_obj = self.env['product.pricelist.item'].browse(rule_id)
        if rule_obj.price_discount == -1.0 and rule_obj.price_surcharge != 0.0:  # es un net
            price = rule_obj.price_surcharge
            if self.env.uid == SUPERUSER_ID and self.env.context.get('company_id'):
                taxes = product_obj.taxes_id.filtered(lambda r: r.company_id.id == self.env.context['company_id'])
            else:
                taxes = product_obj.taxes_id
            tax_obj = self.env['account.tax']
            price = tax_obj._fix_tax_included_price(price, taxes, res['value']['taxes_id'])

            discount = 0.0
        else:
            price = base_price
            if price > 0:
                discount = (1.0 - price_net / price) * 100.0
            else:
                discount = 0.0

        res['value']['discount'] = discount
        res['value']['price_unit'] = price

        return res


class stock_move(models.Model):
    _inherit = "stock.move"

    @api.model
    def _get_invoice_line_vals(self, move, partner, inv_type):
        res = super(stock_move, self)._get_invoice_line_vals(move, partner,
                                                            inv_type)
        if move.purchase_line_id:
            res['discount'] = move.purchase_line_id.discount
        return res


#TODO: falta crar onchange ethod al camp quantity perque amb una tarrifa amb quantitats canmvii el preu.
# # El calcul dels decomptes canviat el produt_id funcona ok
"""
class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
            company_id=None):

        res = super(account_invoice_line, self).product_id_change(product, uom_id, qty, name, type,
            partner_id, fposition_id, price_unit, currency_id, company_id)

        if not product:
            return res

        product_obj = self.env['product.product'].browse(product)

        partner_obj = self.env['res.partner'].browse(partner_id)

        if type in ('in_invoice', 'in_refund'):
            pricelist_obj = partner_obj.property_product_pricelist_purchase
        else:
            pricelist_obj = partner_obj.property_product_pricelist

        #pricelist_obj = self.env['product.pricelist'].browse(pricelist_id)
        list_price, price_net, rule_id = pricelist_obj.price_rule_get2(product, qty or 1.0, partner_id)[pricelist_obj.id]

        rule_obj = self.env['product.pricelist.item'].browse(rule_id)
        if rule_obj.price_discount == -1.0 and rule_obj.price_surcharge != 0.0:  # es un net
            price = rule_obj.price_surcharge
            if self.env.uid == SUPERUSER_ID and self.env.context.get('company_id'):
                taxes = product_obj.taxes_id.filtered(lambda r: r.company_id.id == self.env.context['company_id'])
            else:
                taxes = product_obj.taxes_id
            tax_obj = self.env['account.tax']
            price = tax_obj._fix_tax_included_price(price, taxes, res['value']['invoice_line_tax_id'])

            discount = 0.0
        else:
            price = list_price
            if price > 0:
                discount = (1.0 - price_net / price) * 100.0
            else:
                discount = 0.0

        res['value']['discount'] = discount
        res['value']['price_unit'] = price

        return res
"""





