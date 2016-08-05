# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2013 Camptocamp SA
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

from openerp import models, fields, api, _
from openerp.exceptions import AccessError, Warning, ValidationError


def _reopen(self, data={}):
    return {
        'type': 'ir.actions.act_window',
        'view_mode': 'form',
        'view_type': 'form',
        'res_id': self.id,
        'res_model': self._name,
        'target': 'new',
        # save original model in context,
        # because selecting the list of available
        # templates requires a model in context
        'context': {
            'default_model': self._name,
            'data': data,
        },
    }

class Product(models.Model):
    _inherit = 'product.product'

    group_id = fields.Many2one(comodel_name='product.relation.group', ondelete='restrict')

    cost_avg = fields.Float(string='Cost', compute='_compute_cost_avg', store=True)

    product_related_ids = fields.One2many(comodel_name='product.relation.group.rel', compute='_compute_product_related')

    @api.depends('group_id', 'group_id.product_related_ids')
    def _compute_product_related(self):
        self.product_related_ids = self.group_id.product_related_ids.sorted(lambda x: (0 if x.product_id.id == self.id else 1, self.cost_avg)) #.filtered(lambda x: x.product_id.id != self.id)


    @api.depends('standard_price', 'seller_ids.pricelist_ids', 'seller_ids.name.property_product_pricelist_purchase.version_id.items_id')
    def _compute_cost_avg(selfs):
        for self in selfs:
            self.cost_avg = self.standard_price
            if self.cost_avg == 0.0:
                n = 0
                price_acum = 0
                for s in self.seller_ids:
                    if len(s.pricelist_ids)>0:
                        pricelist_obj = s.name.property_product_pricelist_purchase
                        price, dummy = pricelist_obj.price_rule_get(self.id, 1.0, s.name.id)[pricelist_obj.id]
                        price_acum += price
                        n += 1

                if n>0:
                    self.cost_avg = price_acum/n

    @api.multi
    def button_add(self):
        return {
            'type': 'ir.actions.act_window',
            'name':_("Add related product"),
            'res_model': 'product.relation.add.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            #'views': [(view.id, 'form')],
            #'view_id': view.id,
            #'res_id': wizard_id.id,
            'target': 'new',
            #'context': context,
        }

    @api.multi
    def button_refresh_costs(self):
        for p in self.group_id.product_related_ids:
            p.product_id._compute_cost_avg()


class ProductRelationGroupRel(models.Model):
    _name = 'product.relation.group.rel'
    _order = 'group_id, cost_avg'

    product_id = fields.Many2one(string='Product', comodel_name='product.product', required=True, ondelete='restrict')
    qty_available = fields.Float(related='product_id.qty_available')

    cost_avg = fields.Float(string='Cost', related='product_id.cost_avg', store=True)

    group_id = fields.Many2one(string='Group', comodel_name='product.relation.group', required=True, ondelete='restrict')

    _sql_constraints = [('Unique product', 'unique (product_id)', _('Each product must belong to one group only'))]

    @api.multi
    def button_remove(self):
        if len(self.group_id.product_related_ids) == 2:
            pr1 = self.group_id.product_related_ids.filtered(lambda x: x.id != self.id)
            pr1.product_id.group_id = False
            pr1.unlink()

            self.product_id.group_id = False
            g = self.group_id
            self.unlink()
            g.unlink()

        elif len(self.group_id.product_related_ids) == 1:
            self.product_id.group_id = False
            g = self.group_id
            self.unlink()
            g.unlink()
        else:
            self.product_id.group_id = False
            self.unlink()


class ProductRelationGroup(models.Model):
    _name = 'product.relation.group'

    product_related_ids = fields.One2many(comodel_name='product.relation.group.rel', inverse_name='group_id')


class WizardProductRelationAdd(models.TransientModel):
    _name = 'product.relation.add.wizard'

    product_id = fields.Many2one(string='Product', comodel_name='product.product', required=True)

    msg = fields.Char()

    state = fields.Selection(selection=[('add', 'Add'), ('merge', 'Merge')],
                             string='Status', readonly=True, default='add')

    @api.multi
    def button_add(self):
        product0_obj = self.env[self.env.context.get('active_model')].browse(self.env.context['active_ids'])
        # el producte es el mateix de la fitxa del producte actiu
        if product0_obj.id == self.product_id.id:
            raise ValidationError(_('This is the source product itself'))

        # el producte ja existeix el la llsyta
        tmp_obj = product0_obj.group_id.product_related_ids.filtered(lambda x: x.product_id.id == self.product_id.id)
        if tmp_obj:
            raise ValidationError(_('The product selected is already added'))

        if not self.product_id.group_id and not product0_obj.group_id:
            group9_obj = self.env['product.relation.group'].create({})
            group9_obj.product_related_ids = [(0, 0, {'product_id': self.product_id.id}),
                                              (0, 0, {'product_id': product0_obj.id})]
            self.product_id.group_id = product0_obj.group_id = group9_obj.id
        elif not self.product_id.group_id and product0_obj.group_id:
            product0_obj.group_id.product_related_ids = [(0, 0, {'product_id': self.product_id.id})]
            self.product_id.group_id = product0_obj.group_id.id
        elif self.product_id.group_id and not product0_obj.group_id:
            self.product_id.group_id.product_related_ids = [(0, 0, {'product_id': product0_obj.id})]
            product0_obj.group_id = self.product_id.group_id.id
        else:
            if self.product_id.group_id.id!=product0_obj.group_id.id:
                self.state = 'merge'
                self.msg = _('The product belong to another group. Would you like to merge both groups?')

                return _reopen(self, data={'product0_id': product0_obj.id })

    @api.multi
    def button_merge(self):
        product0_obj = self.env['product.product'].browse(self.env.context.get('data')['product0_id'])

        tmp_group = self.product_id.group_id
        for pr in self.product_id.group_id.product_related_ids:
            pr.product_id.group_id = pr.group_id = product0_obj.group_id.id
        tmp_group.unlink()
