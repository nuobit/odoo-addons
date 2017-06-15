# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today OpenERP SA (<http://www.openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

'''
from openerp.osv import osv, fields, expression
import openerp.addons.decimal_precision as dp
'''
from openerp import models, fields, api, _
from openerp.exceptions import AccessError, Warning, ValidationError, except_orm

class product_pricelist1(models.Model):
    _inherit = "product.pricelist"

    '''
    @api.v7
    def _price_rule_get_multi(self, cr, uid, pricelist, products_by_qty_by_partner, context=None):
        return super(product_pricelist, self)._price_rule_get_multi(cr, uid, pricelist, products_by_qty_by_partner, context)


    @api.v8
    def _price_rule_get_multi(self, products_by_qty_by_partner):
        return product_pricelist._price_rule_get_multi(
            self._model, self._cr, self._uid, self, products_by_qty_by_partner, context=self._context)

    '''


class product_pricelist(models.Model):
    _inherit = "product.pricelist"

    sequence = fields.Integer('Sequence', required=True, default=5,
                               help="Gives the order in which the pricelist will be checked. The evaluation gives highest priority to lowest sequence")

    '''
    @api.v7
    def _price_rule_get_multi(self, cr, uid, pricelist, products_by_qty_by_partner, context=None):
        prl = super(product_pricelist, self)._price_rule_get_multi(cr, uid, pricelist, products_by_qty_by_partner,
                                                                   context)

        d = {}
        for product_id, (price, rule_id) in prl.items():
            rule_obj = self.pool.get('product.pricelist.item').browse(cr, uid, rule_id, context=context)

            if rule_obj.base == -1:
                if rule_obj.base_pricelist_id.sequence < self.sequence:
                    a = 1

            d[product_id] = (price, rule_id)

        return d
    '''

    '''
    @api.v7
    def _price_rule_get_multi(self, cr, uid, pricelist, products_by_qty_by_partner, context=None):
        prl = super(product_pricelist, self)._price_rule_get_multi(cr, uid, pricelist, products_by_qty_by_partner, context)

        return self.foo(cr, uid, pricelist, prl, context )

    @api.v7
    def foo(self, cr, uid, ids, prl, context = None):
        records = self.browse(cr, uid, ids, context)

        return product_pricelist.foo(records, prl)


    @api.v8
    def foo(self, prl):
        d = {}
        for product_id, (price, rule_id) in prl.items():
            rule_obj = self.env['product.pricelist.item'].browse(rule_id)

            if rule_obj.base == -1:
                if rule_obj.base_pricelist_id.sequence < self.sequence:
                    a=1

            d[product_id] = (price, rule_id)

        return d

    '''

    '''
        prl = self._price_rule_get_multi([(product, quantity, partner)]).get(product.id, False)
        if prl:
            _, rule_id = prl
            rule_obj = self.env['product.pricelist.item'].browse(rule_id)
            return rule_obj.price_discount == -1.0 and rule_obj.price_surcharge != 0.0

        return False



        return prl
    '''




