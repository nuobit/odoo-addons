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

    group_id = fields.Many2one(comodel_name='product.relation.group')

    product_related_ids = fields.One2many(related='group_id.product_related_ids', store=False)


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
    def button_remove(self):
        for pr in self.group_id.product_related_ids:
            if pr.mark:
                pr.product_id.group_id=False
                pr.unlink()

        if len(self.group_id.product_related_ids) == 1:
            self.group_id.product_related_ids.unlink()
            self.group_id.unlink()
        elif len(self.group_id.product_related_ids) == 0:
            self.group_id.unlink()



class ProductRelationGroupRel(models.Model):
    _name = 'product.relation.group.rel'

    product_id = fields.Many2one(comodel_name='product.product', required=True, ondelete='restrict')
    group_id = fields.Many2one(comodel_name='product.relation.group', required=True, ondelete='restrict')
    mark = fields.Boolean(string='Mark')

    _sql_constraints = [('Unique product', 'unique (product_id)', _('Each product must belong to one group only'))]



class ProductRelationGroup(models.Model):
    _name = 'product.relation.group'

    product_related_ids = fields.One2many(comodel_name='product.relation.group.rel', inverse_name='group_id')




class WizardProductRelationAdd(models.TransientModel):
    _name = 'product.relation.add.wizard'

    product_id = fields.Many2one(comodel_name='product.product', required=True)

    msg = fields.Char()

    state = fields.Selection(selection=[('adding', 'Adding'), ('merge', 'Merge')],
                             string='Status', readonly=True, default='adding')

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

"""

class Product(models.Model):
    _inherit = 'product.product'

    relation_group_id = fields.Many2one(comodel_name='product.relation.group')


class ProductRelationGroup(models.Model):
    _name = 'product.relation.group'
    _rec_name = 'id'

    @api.model
    def get_relation_type_selection(self):
        # selection can be inherited and extended
        return [('cross_sell', 'Cross-Sell'),
                ('up_sell', 'Up-Sell'),
                #('related', 'Related')
                ]

    type = fields.Selection(
        selection='get_relation_type_selection',
        string='Type',
        required=True, default='cross_sell')
    is_active = fields.Boolean('Active', default=True)

    description = fields.Text('Description')

    product_ids = fields.Many2many(
        comodel_name='product.product',
        relation = 'product_relation_group_product_rel',
        column1 = 'relation_group_id',
        column2 = 'product_id',
        string='Products',
    )

    test_ids = fields.Many2one(
        comodel_name='product.product',
        string='Products1',
    )

    @api.multi
    @api.constrains('product_ids')
    def _check_products(self):
        for rec in self:
            if not rec.product_ids:
                raise ValidationError("Product list cannot be null.")
            else:
                for product in rec.product_ids:
                    self.env.cr.execute('SELECT relation_group_id '
                                        'FROM product_relation_group_product_rel '
                                        'WHERE relation_group_id!=%s AND '
                                        '      product_id=%s', (rec.id, product.id))
                    res = self.env.cr.fetchone()
                    if res is not None:
                        relation_group_id = res[0]
                        #pr = self.env['product.relation.group'].browse(relation_group_id)
                        raise ValidationError("El producte %s ja existeis en el grup num %i" % (product.default_code, relation_group_id))


    @api.multi
    def merge(self):
        wizard_id = self.env['pr.wizard'].create({'name':'com mola popular'})
        return {
            'type': 'ir.actions.act_window',
            'name':_("Display Name"),#Name You want to display on wizard
            'res_model': 'pr.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            #'views': [(view.id, 'form')],
            #'view_id': view.id,
            'res_id': wizard_id.id,
            'target': 'new',
            #'context': context,
        }

class ProductRelationGroupRel(models.Model):
    _name = 'product.relation.group.product.rel'

    relation_group_id = fields.Many2one('product.relation.group')
    product_id = fields.Many2one('product.product')


class WizardPr(models.TransientModel):
    _name = 'pr.wizard'


    name = fields.Char('Name')

    @api.model
    def my_method(self, product_id):
        return {'hello': 'world', 'id': self.id, 'product_id': product_id}

"""
"""
class ProductRelation(models.Model):
    _name = 'product.relation'
    _rec_name = 'id'

    @api.model
    def get_relation_type_selection(self):
        # selection can be inherited and extended
        return [('cross_sell', 'Cross-Sell'),
                ('up_sell', 'Up-Sell'),
                #('related', 'Related')
                ]

    type = fields.Selection(
        selection='get_relation_type_selection',
        string='Type',
        required=True, default='cross_sell')
    is_active = fields.Boolean('Active', default=True)

    description = fields.Text('Description')

    product_ids = fields.Many2many(
        comodel_name='product.product',
        #relation = 'product_relation_rel',
        #column1 = 'relation_id',
        #column2 = 'product_id',
        string='Products')


    @api.one
    @api.constrains('product_ids')
    def _check_products(self):
        if not self.product_ids:
            raise ValidationError("Product list cannot be null.")
        else:
            pass
            '''
            for product in self.product_ids:
                pr = self.env['product.relation.rel'].search_count([('relation_id', '!=', self.id),
                                                                    ('product_id', '=', product.id)
                                                                   ])
                if pr != 0:
                   raise ValidationError("El producte ja existeis en eun altres grups. utiizeu el buto merge per fusonaros si sescau")
                   '''




    @api.multi
    def merge(self):
        pr5 = []

        for product in self.product_ids:
            '''
            pr = self.env['product.relation.rel'].search([('relation_id', '!=', self.id),
                                                          ('product_id', '=', product.id)
                                                         ])
            if pr:
                #for pr0 in pr:
                #    pr5.append()
                pass

            '''
            pass


        wizard_id = self.env['pr.wizard'].create({'name':'com mola popular'})
        return {
            'type': 'ir.actions.act_window',
            'name':_("Display Name"),#Name You want to display on wizard
            'res_model': 'pr.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            #'views': [(view.id, 'form')],
            #'view_id': view.id,
            'res_id': wizard_id.id,
            'target': 'new',
            #'context': context,
        }

'''
class ProductRelationRel(models.Model):
    _name = 'product.relation.rel'

    relation_id = fields.Many2one(comodel_name='product.relation')
    product_id = fields.Many2one(comodel_name='product.product')

    #_sql_constraints = [
    #    ('product_in_one_group', 'unique(product_id)', 'A product can only be in one relation group.'),
    #]
'''



class WizardPr(models.TransientModel):
    _name = 'pr.wizard'


    name = fields.Char('Name')

    product_pr_prod_ids = fields.One2many(
        comodel_name='pr.wizard.prod',
        inverse_name='product_pr_id',
        string='Product relations1',
        readonly=True
        )





class WizardPrProd(models.TransientModel):
    _name = 'pr.wizard.prod'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product'
    )
    relation_id = fields.Many2one(
        comodel_name='product.relation',
        string='Relation'
    )

    product_pr_id = fields.Many2one(
        comodel_name='pr.wizard',
        string='Product relations2',
        )
"""
