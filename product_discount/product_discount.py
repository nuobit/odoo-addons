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
        price_net, rule_id = pricelist_obj.price_rule_get(product, qty or 1.0, partner_id)[pricelist]

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
        list_price, price_net, rule_id = pricelist_obj.price_rule_get2(product_id, qty or 1.0, partner_id)[pricelist_id]

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
            price = list_price
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




class product_pricelist(models.Model):
    _inherit = "product.pricelist"

    def _price_rule_get_multi2(self, cr, uid, pricelist, products_by_qty_by_partner, context=None):
        context = context or {}
        date = context.get('date') or time.strftime('%Y-%m-%d')
        date = date[0:10]

        products = map(lambda x: x[0], products_by_qty_by_partner)
        currency_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.template')
        product_uom_obj = self.pool.get('product.uom')
        price_type_obj = self.pool.get('product.price.type')

        if not products:
            return {}

        version = False
        for v in pricelist.version_id:
            if ((v.date_start is False) or (v.date_start <= date)) and ((v.date_end is False) or (v.date_end >= date)):
                version = v
                break
        if not version:
            raise osv.except_osv(_('Warning!'),
                                 _("At least one pricelist has no active version !\nPlease create or activate one."))
        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = categ_ids.keys()

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        # Load all rules
        cr.execute(
            'SELECT i.id '
            'FROM product_pricelist_item AS i '
            'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = any(%s)) '
            'AND (product_id IS NULL OR (product_id = any(%s))) '
            'AND ((categ_id IS NULL) OR (categ_id = any(%s))) '
            'AND (price_version_id = %s) '
            'ORDER BY sequence, min_quantity desc',
            (prod_tmpl_ids, prod_ids, categ_ids, version.id))

        item_ids = [x[0] for x in cr.fetchall()]
        items = self.pool.get('product.pricelist.item').browse(cr, uid, item_ids, context=context)

        price_types = {}

        results = {}
        for product, qty, partner in products_by_qty_by_partner:
            results[product.id] = 0.0
            rule_id = False
            price = False
            list_price = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = product_uom_obj._compute_qty(
                        cr, uid, context['uom'], qty, product.uom_id.id or product.uos_id.id)
                except except_orm:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            for rule in items:
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (
                            product.product_variant_count == 1 and product.product_variant_ids[0].id == rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.base == -1:
                    if rule.base_pricelist_id:
                        price_tmp = self._price_get_multi(cr, uid,
                                                          rule.base_pricelist_id, [(product,
                                                                                    qty, partner)], context=context)[
                            product.id]
                        ptype_src = rule.base_pricelist_id.currency_id.id
                        price_uom_id = qty_uom_id
                        price = currency_obj.compute(cr, uid,
                                                     ptype_src, pricelist.currency_id.id,
                                                     price_tmp, round=False,
                                                     context=context)
                elif rule.base == -2:
                    seller = False
                    for seller_id in product.seller_ids:
                        if (not partner) or (seller_id.name.id != partner):
                            continue
                        seller = seller_id
                    if not seller and product.seller_ids:
                        seller = product.seller_ids[0]
                    if seller:
                        qty_in_seller_uom = qty
                        seller_uom = seller.product_uom.id
                        if qty_uom_id != seller_uom:
                            qty_in_seller_uom = product_uom_obj._compute_qty(cr, uid, qty_uom_id, qty, to_uom_id=seller_uom)
                        price_uom_id = seller_uom
                        for line in seller.pricelist_ids:
                            if line.min_quantity <= qty_in_seller_uom:
                                price = line.price

                else:
                    if rule.base not in price_types:
                        price_types[rule.base] = price_type_obj.browse(cr, uid, int(rule.base))
                    price_type = price_types[rule.base]

                    # price_get returns the price in the context UoM, i.e. qty_uom_id
                    price_uom_id = qty_uom_id
                    price = currency_obj.compute(
                        cr, uid,
                        price_type.currency_id.id, pricelist.currency_id.id,
                        product_obj._price_get(cr, uid, [product], price_type.field, context=context)[product.id],
                        round=False, context=context)

                list_price = price
                if price is not False:
                    price_limit = price
                    price = price * (1.0 + (rule.price_discount or 0.0))
                    if rule.price_round:
                        price = tools.float_round(price, precision_rounding=rule.price_round)

                    convert_to_price_uom = (lambda price: product_uom_obj._compute_price(
                        cr, uid, product.uom_id.id,
                        price, price_uom_id))
                    if rule.price_surcharge:
                        price_surcharge = convert_to_price_uom(rule.price_surcharge)
                        price += price_surcharge

                    if rule.price_min_margin:
                        price_min_margin = convert_to_price_uom(rule.price_min_margin)
                        price = max(price, price_limit + price_min_margin)

                    if rule.price_max_margin:
                        price_max_margin = convert_to_price_uom(rule.price_max_margin)
                        price = min(price, price_limit + price_max_margin)

                    rule_id = rule.id
                break

            # Final price conversion to target UoM
            price = product_uom_obj._compute_price(cr, uid, price_uom_id, price, qty_uom_id)

            results[product.id] = (list_price, price, rule_id)
        return results


    def price_rule_get_multi2(self, cr, uid, ids, products_by_qty_by_partner, context=None):
        """multi products 'price_get'.
           @param ids:
           @param products_by_qty:
           @param partner:
           @param context: {
             'date': Date of the pricelist (%Y-%m-%d),}
           @return: a dict of dict with product_id as key and a dict 'price by pricelist' as value
        """
        if not ids:
            ids = self.pool.get('product.pricelist').search(cr, uid, [], context=context)
        results = {}
        for pricelist in self.browse(cr, uid, ids, context=context):
            subres = self._price_rule_get_multi2(cr, uid, pricelist, products_by_qty_by_partner, context=context)
            for product_id,price in subres.items():
                results.setdefault(product_id, {})
                results[product_id][pricelist.id] = price
        return results


    def price_rule_get2(self, cr, uid, ids, prod_id, qty, partner=None, context=None):
        product = self.pool.get('product.product').browse(cr, uid, prod_id, context=context)
        res_multi = self.price_rule_get_multi2(cr, uid, ids, products_by_qty_by_partner=[(product, qty, partner)], context=context)
        res = res_multi[prod_id]
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





