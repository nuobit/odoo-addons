# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError

OP_SEL = [('and', _('And')), ('or', _('Or'))]


def and2or(domain):
    return ['|'] * (len(domain) - 1) + domain


def prepare_in_domain(fields, in_objs, in_op):
    domain_in = []
    if in_objs:
        for obj in in_objs:
            domain_in_tmp = []
            for field in fields:
                domain_in_tmp.append((field, '=', obj.id))
            domain_in += and2or(domain_in_tmp)

        if in_op == 'or':
            domain_in = and2or(domain_in)

    return domain_in


class LightingProductAdvancedSearch(models.TransientModel):
    """
    This wizard will allow to make complex searches over products
    """
    _name = "lighting.product.advanced.search"
    _description = "Advanced search for products"

    # attachment search
    attachment_type_in_ids = fields.Many2many(string='Types',
                                              comodel_name='lighting.attachment.type',
                                              relation='lighting_product_advanced_search_attachment_type_in_rel',
                                              column1='advanced_search_id',
                                              column2='type_id')
    attachment_type_in_op = fields.Selection(string='Operator', selection=OP_SEL, default='and')
    attachment_type_not_in_ids = fields.Many2many(string='Types', comodel_name='lighting.attachment.type',
                                                  relation='lighting_product_advanced_search_attachment_type_not_in_rel',
                                                  column1='advanced_search_id',
                                                  column2='type_id')
    attachment_type_not_in_op = fields.Selection(string='Operator', selection=OP_SEL, default='and')

    # application search
    application_in_ids = fields.Many2many(string='Applications', comodel_name='lighting.product.application',
                                          relation='lighting_product_advanced_search_application_in_rel',
                                          column1='advanced_search_id',
                                          column2='application_id')
    application_in_op = fields.Selection(string='Operator', selection=OP_SEL, default='and')

    # finish search
    finish_in_ids = fields.Many2many(string='Finishes', comodel_name='lighting.product.finish',
                                     relation='lighting_product_advanced_search_finish_in_rel',
                                     column1='advanced_search_id',
                                     column2='finish_id')

    # lampholder search
    lampholder_in_ids = fields.Many2many(string='Lampholders', comodel_name='lighting.product.source.lampholder',
                                         relation='lighting_product_advanced_search_lampholder_in_rel',
                                         column1='advanced_search_id',
                                         column2='lampholder_id')
    lampholder_in_op = fields.Selection(string='Operator', selection=OP_SEL, default='and')

    # source type search
    source_type_in_ids = fields.Many2many(string='Source types', comodel_name='lighting.product.source.type',
                                          relation='lighting_product_advanced_search_source_type_in_rel',
                                          column1='advanced_search_id',
                                          column2='source_type_id')
    source_type_in_op = fields.Selection(string='Operator', selection=OP_SEL, default='and')

    # body material search
    body_material_in_ids = fields.Many2many(string='Body materials', comodel_name='lighting.product.material',
                                            relation='lighting_product_advanced_search_body_material_in_rel',
                                            column1='advanced_search_id',
                                            column2='body_material_id')
    body_material_in_op = fields.Selection(string='Operator', selection=OP_SEL, default='and')

    # input/output voltage
    voltage_in_ids = fields.Many2many(string='Voltages', comodel_name='lighting.product.voltage',
                                      relation='lighting_product_advanced_search_voltage_in_rel',
                                      column1='advanced_search_id',
                                      column2='voltage_id')
    voltage_in_op = fields.Selection(string='Operator', selection=OP_SEL, default='and')

    # IP search
    ip_from_in = fields.Integer(string='From')
    ip_to_in = fields.Integer(string='To')

    # wattage
    wattage_from_in = fields.Float(string='From')
    wattage_to_in = fields.Float(string='To')

    # luminous flux
    luminous_flux_from_in = fields.Integer(string='From')
    luminous_flux_to_in = fields.Integer(string='To')

    # color temperature
    color_temperature_from_in = fields.Integer(string='From')
    color_temperature_to_in = fields.Integer(string='To')

    @api.multi
    def advanced_search(self):
        domain = []

        # application
        domain += prepare_in_domain(['application_ids'], self.application_in_ids, self.application_in_op)

        # finish
        domain += prepare_in_domain(['finish_id'], self.finish_in_ids, 'or')

        # marketing/technical lampholder
        domain += prepare_in_domain(['source_ids.lampholder_id', 'source_ids.lampholder_technical_id'],
                                    self.lampholder_in_ids, self.lampholder_in_op)

        # source type
        domain += prepare_in_domain(['source_ids.line_ids.type_id'], self.source_type_in_ids, self.source_type_in_op)

        # body material
        domain += prepare_in_domain(['body_material_ids'], self.body_material_in_ids, self.body_material_in_op)

        # input/output voltage
        domain += prepare_in_domain(['input_voltage_id', 'output_voltage_id'], self.voltage_in_ids, self.voltage_in_op)

        # ip
        if self.ip_from_in:
            if self.ip_to_in:
                domain += [('ip', '>=', self.ip_from_in),
                           ('ip', '<=', self.ip_to_in)]
            else:
                domain += [('ip', '=', self.ip_from_in)]

        # wattage
        if self.wattage_from_in:
            if self.wattage_to_in:
                domain += [('source_ids.line_ids.wattage', '>=', self.wattage_from_in),
                           ('source_ids.line_ids.wattage', '<=', self.wattage_to_in)]
            else:
                domain += [('source_ids.line_ids.wattage', '=', self.wattage_in)]

        # luminous fllux
        if self.luminous_flux_from_in:
            if self.luminous_flux_to_in:
                domain += [('source_ids.line_ids.luminous_flux1', '>=', self.luminous_flux_from_in),
                           ('source_ids.line_ids.luminous_flux1', '<=', self.luminous_flux_to_in)]
            else:
                domain += [('source_ids.line_ids.luminous_flux1', '=', self.luminous_flux_from_in)]

        # color temperature
        if self.color_temperature_from_in:
            if self.color_temperature_to_in:
                domain += [('source_ids.line_ids.color_temperature', '>=', self.color_temperature_from_in),
                           ('source_ids.line_ids.color_temperature', '<=', self.color_temperature_to_in)]
            else:
                domain += [('source_ids.line_ids.color_temperature', '=', self.color_temperature_from_in)]

        # attachment
        domain_in = []
        if self.attachment_type_in_ids:
            for attachment_type_id in self.attachment_type_in_ids:
                domain_in.append(('attachment_ids.type_id.id', '=', attachment_type_id.id))
            if self.attachment_type_in_op == 'or':
                domain_in = ['|'] * (len(domain_in) - 1) + domain_in

            domain += domain_in

        domain_not_in = []
        if self.attachment_type_not_in_ids:
            domain_not_in_tmp = []
            for attachment_type_id in self.attachment_type_not_in_ids:
                domain_not_in_tmp.append(('type_id.id', '=', attachment_type_id.id))
            if self.attachment_type_not_in_op == 'and':
                domain_not_in_tmp = ['|'] * (len(domain_not_in_tmp) - 1) + domain_not_in_tmp

            attachment_ids = self.env['lighting.attachment'].search(domain_not_in_tmp)
            domain_not_in = [('id', 'not in', attachment_ids.mapped('product_id.id'))]

            domain += domain_not_in

        return {
            'name': _("Advanced Search"),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'lighting.product',
            'type': 'ir.actions.act_window',
            'domain': domain,
        }
