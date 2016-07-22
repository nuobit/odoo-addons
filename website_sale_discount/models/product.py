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

#from openerp.osv import osv

class product_pricelist(models.Model):
    _inherit = "product.pricelist"

    @api.v7
    def _price_rule_get_multi(self, cr, uid, pricelist, products_by_qty_by_partner, context=None):
         return super(product_pricelist, self)._price_rule_get_multi(cr, uid, pricelist, products_by_qty_by_partner, context)

    @api.v8
    def _price_rule_get_multi(self, products_by_qty_by_partner):
       return product_pricelist._price_rule_get_multi(
            self._model, self._cr, self._uid, self, products_by_qty_by_partner, context=self._context)

    def _is_net_get_multi(self, product, quantity, partner):
        prl = self._price_rule_get_multi([(product, quantity, partner)]).get(product.id, False)
        if prl:
            _, rule_id = prl
            rule_obj = self.env['product.pricelist.item'].browse(rule_id)
            return rule_obj.price_discount == -1.0 and rule_obj.price_surcharge!=0.0

        return False

class product_template(models.Model):
    _inherit = "product.template"

    discount = fields.Float(string="Discount", compute='_compute_discount')
    is_net = fields.Boolean(string="Net", compute='_compute_is_net', default=False)

    @api.depends('price', 'lst_price')
    def _compute_discount(self):
        for rec in self:
            if rec.price and rec.lst_price:
                rec.discount = (1-rec.price/rec.lst_price)*100
            else:
                rec.discount = False

    @api.multi
    def _compute_is_net(self):
        pricelist = self.env.context.get('pricelist', False)
        if pricelist:
            plobj = self.env['product.pricelist']
            # Support context pricelists specified as display_name or ID for compatibility
            if isinstance(pricelist, basestring):
                pricelist_ids = plobj.name_search(name=pricelist, operator='=', limit=1)
                pricelist = pricelist_ids[0][0] if pricelist_ids else pricelist
            if isinstance(pricelist, (int, long)):
                quantity = self.env.context.get('quantity') or 1.0
                partner = self.env.context.get('partner', False)
                pl = plobj.browse(pricelist)
                for product in self:
                    product.is_net = pl._is_net_get_multi(product, quantity, partner)





class product_product(models.Model):
    _inherit = "product.product"

    discount = fields.Float(string="Discount", compute='_compute_discount')
    is_net = fields.Boolean(string="Net", compute='_compute_is_net', default=False)

    @api.depends('price', 'lst_price')
    def _compute_discount(self):
        for rec in self:
            if rec.price and rec.lst_price:
                rec.discount = (1-rec.price/rec.lst_price)*100
            else:
                rec.discount = False

    @api.multi
    def _compute_is_net(self):
        pricelist = self.env.context.get('pricelist', False)
        if pricelist:
            plobj = self.env['product.pricelist']
            # Support context pricelists specified as display_name or ID for compatibility
            if isinstance(pricelist, basestring):
                pricelist_ids = plobj.name_search(name=pricelist, operator='=', limit=1)
                pricelist = pricelist_ids[0][0] if pricelist_ids else pricelist
            if isinstance(pricelist, (int, long)):
                quantity = self.env.context.get('quantity') or 1.0
                partner = self.env.context.get('partner', False)
                pl = plobj.browse(pricelist)
                for product in self:
                    product.is_net = pl._is_net_get_multi(product, quantity, partner)




