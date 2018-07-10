# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError

OP_SEL = [('and', _('And')), ('or', _('Or'))]

class LightingProductAdvancedSearch(models.TransientModel):
    """
    This wizard will allow to make complex searches over products
    """
    _name = "lighting.product.advanced.search"
    _description = "Advanced search for products"

    type_in_ids = fields.Many2many(comodel_name='lighting.attachment.type',
                                   relation='lighting_product_advanced_search_attachment_type_in_rel',
                                   column1='advanced_search_id',
                                   column2='type_id')
    type_in_op = fields.Selection(selection=OP_SEL, string='Operator', default='and')
    type_not_in_ids = fields.Many2many(comodel_name='lighting.attachment.type',
                                       relation='lighting_product_advanced_search_attachment_type_not_in_rel',
                                       column1='advanced_search_id',
                                       column2='type_id')
    type_not_in_op = fields.Selection(selection=OP_SEL, string='Operator', default='and')

    '''@api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '%s (%s)' % (record.name, 'record.type_id.display_name')
            vals.append((record.id, name))

        return vals
    '''

    @api.multi
    def advanced_search(self):
        domain_in = []
        if self.type_in_ids:
            for type_id in self.type_in_ids:
                domain_in.append(('attachment_ids.type_id.id', '=', type_id.id))
            if self.type_in_op == 'or':
                domain_in = ['|']*(len(domain_in)-1) + domain_in

        domain_not_in = []
        if self.type_not_in_ids:
            domain_not_in_tmp = []
            for type_id in self.type_not_in_ids:
                domain_not_in_tmp.append(('type_id.id', '=', type_id.id))
            if self.type_not_in_op == 'and':
                domain_not_in_tmp = ['|']*(len(domain_not_in_tmp)-1) + domain_not_in_tmp

            attachment_ids = self.env['lighting.attachment'].search(domain_not_in_tmp)
            domain_not_in = [('id', 'not in', attachment_ids.mapped('product_id.id'))]

        domain = domain_in + domain_not_in

        return {
            'name': _("Advanced Search"),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'lighting.product',
            'type': 'ir.actions.act_window',
            'domain': domain,
        }
