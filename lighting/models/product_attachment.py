# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingAttachment(models.Model):
    _name = 'lighting.attachment'
    _order = 'type_id'

    name = fields.Char(string='Description', translate=True)
    type_id = fields.Many2one(comodel_name='lighting.attachment.type', ondelete='restrict', required=True,
                              string='Type')

    datas = fields.Binary(string="Document", attachment=True, required=True)
    datas_fname = fields.Char(string='Filename', required=True)
    attachment_id = fields.Many2one(comodel_name='ir.attachment',
                                    compute='_compute_ir_attachment', readonly=True)

    date = fields.Date(string='Date')
    is_default = fields.Boolean(string='Default')

    @api.depends('datas')
    def _compute_ir_attachment(self):
        for rec in self:
            attachment_obj = rec.env['ir.attachment'].search([('res_field', '=', 'datas'),
                                                              ('res_id', '=', rec.id),
                                                              ('res_model', '=', rec._name)])
            if attachment_obj:
                rec.attachment_id = attachment_obj[0]
            else:
                rec.attachment_id = False

    lang_id = fields.Many2one(comodel_name='lighting.language', ondelete='restrict', string='Language')

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '%s (%s)' % (record.datas_fname, record.type_id.display_name)
            vals.append((record.id, name))

        return vals


class LightingAttachmentType(models.Model):
    _name = 'lighting.attachment.type'
    _order = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', translate=True)

    _sql_constraints = [('name_uniq', 'unique (code)', 'The attachment type description must be unique!'),
                        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            if record.name:
                name = '%s (%s)' % (record.name, record.code)
            else:
                name = record.code

            vals.append((record.id, name))

        return vals
