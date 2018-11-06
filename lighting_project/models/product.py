# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LightingProductFamily(models.Model):
    _inherit = 'lighting.product.family'

    project_count = fields.Integer(compute='_compute_project_count', string='Projects(s)')

    def _compute_project_count(self):
        for record in self:
            record.project_count = self.env['lighting.project'].search_count([('family_ids', '=', record.id)])

    @api.multi
    def unlink(self):
        records = self.env['lighting.project'].search([('family_ids', 'in', self.ids)])
        if records:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(LightingProductFamily, self).unlink()


class LightingCatalog(models.Model):
    _inherit = 'lighting.catalog'

    project_ids = fields.Many2many(compute='_compute_project_ids', comodel_name='lighting.project',
                                   string='Projects', readonly=True)

    def _compute_project_ids(self):
        for record in self:
            family_ids = self.env['lighting.product'] \
                .search([('catalog_ids', 'in', record.id)]).mapped('family_ids')
            record.project_ids = self.env['lighting.project'] \
                .search([('family_ids', 'in', family_ids.mapped('id'))])

    project_count = fields.Integer(compute='_compute_project_count', string='Projects(s)')

    def _compute_project_count(self):
        for record in self:
            record.project_count = len(record.project_ids)
