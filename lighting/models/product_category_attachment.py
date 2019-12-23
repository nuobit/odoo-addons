# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductCategoryAttachment(models.Model):
    _name = 'lighting.product.category.attachment'
    _order = 'sequence'
    _rec_name = 'datas_fname'

    name = fields.Text(string='Description', translate=True)

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")

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

    checksum = fields.Char(related='attachment_id.checksum', string='Checksum', readonly=True)

    is_default = fields.Boolean(string='Default')

    brand_id = fields.Many2one(comodel_name='lighting.catalog', ondelete='cascade', string='Brand')
    is_brand_default = fields.Boolean(string="Brand default")

    location_id = fields.Many2one(comodel_name='lighting.product.location', ondelete='cascade', string='Location')
    is_location_default = fields.Boolean(string="Location default")

    category_id = fields.Many2one(comodel_name='lighting.product.category', ondelete='cascade', string='Category')
