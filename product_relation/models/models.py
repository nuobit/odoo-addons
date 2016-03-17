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

'''
class Product(models.Model):
    _inherit = 'product.product'

    relation_group_id = fields.Many2one(comodel_name='product.relation.group')
'''

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