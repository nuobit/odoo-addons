# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingCatalog(models.Model):
    _name = 'lighting.catalog'
    _order = 'name'

    name = fields.Char(string='Catalog', required=True)

    description_show_ip = fields.Boolean(string='Description show IP',
                                         help="If checked, IP and IP2 will be shown on a generated product description "
                                              "for every product in this catalog")

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count([('catalog_ids', '=', record.id)])

    _sql_constraints = [('name_uniq', 'unique (name)', 'The name of catalog must be unique!'),
                        ]

    @api.multi
    def unlink(self):
        records = self.env['lighting.product'].search([('catalog_ids', 'in', self.ids)])
        if records:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(LightingCatalog, self).unlink()
