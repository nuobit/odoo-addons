# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LightingProjectAttachment(models.Model):
    _name = 'lighting.project.attachment'
    _order = 'name'

    name = fields.Text(string='Description', translate=True)

    datas = fields.Binary(string="Document", attachment=True, required=True)
    datas_fname = fields.Char(string='Filename', required=True)
    attachment_id = fields.Many2one(comodel_name='ir.attachment',
                                    compute='_compute_ir_attachment', readonly=True)

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

    is_default = fields.Boolean(string='Default')

    project_id = fields.Many2one(comodel_name='lighting.project', ondelete='cascade', string='Project')