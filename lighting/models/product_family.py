# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductFamily(models.Model):
    _name = 'lighting.product.family'
    _order = 'sequence'

    name = fields.Char(string='Family', required=True)
    code = fields.Char(string='Code', required=False, size=3)
    is_export = fields.Boolean(string='Is export')
    description = fields.Text(string='Description', translate=True)
    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count([('family_ids', '=', record.id)])

    discontinued_product_percent = fields.Float(compute='_compute_discontinued_product_percent',
                                                string='% Discontinued product(s)')

    def _compute_discontinued_product_percent(self):
        for record in self:
            percent = 0
            if record.product_count != 0:
                discontinued_product_count = self.env['lighting.product'].search_count(
                    [('family_ids', '=', record.id), ('state_marketing', '=', 'D')])
                percent = discontinued_product_count / record.product_count * 100
            record.discontinued_product_percent = percent

    attachment_ids = fields.One2many(comodel_name='lighting.product.family.attachment',
                                     inverse_name='family_id', string='Attachments', copy=True,
                                     track_visibility='onchange')
    attachment_count = fields.Integer(compute='_compute_attachment_count', string='Attachment(s)')

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = self.env['lighting.product.family.attachment'] \
                .search_count([('family_id', '=', record.id)])

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The family must be unique!'),
    ]

    @api.multi
    def unlink(self):
        records = self.env['lighting.product'].search([('family_ids', 'in', self.ids)])
        if records:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(LightingProductFamily, self).unlink()
