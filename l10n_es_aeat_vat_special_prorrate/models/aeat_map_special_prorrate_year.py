# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class MapSpecialProrrateYear(models.Model):
    _name = 'aeat.map.special.prorrate.year'

    year = fields.Integer(string="Year", required=True)
    tax_percentage = fields.Float(string="Tax %", required=True)

    tax_final_percentage = fields.Float(string="Final tax %", readonly=True,
                                        compute='_compute_tax_final_percentage')

    @api.depends('year', 'tax_percentage')
    def _compute_tax_final_percentage(self):
        for rec in self:
            next_map = self.search([
                ('company_id', '=', rec.company_id.id),
                ('year', '=', rec.year + 1)
            ])
            if next_map:
                rec.tax_final_percentage = next_map.tax_percentage

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id.id
    )

    _sql_constraints = [
        ('unique_year', 'unique(year, company_id)',
         'AEAT year must be unique'),
    ]

    @api.model
    def get_by_ukey(self, company_id, year):
        return self.search([
            ('company_id', '=', company_id),
            ('year', '=', year),
        ])

    @api.depends('year', 'tax_percentage')
    def name_get(self):
        to_percent_str = lambda x: (x.is_integer() and '%i%%' or '%.2f%%') % x
        result = []
        for rec in self:
            name = [to_percent_str(rec.tax_percentage)]
            if rec.tax_final_percentage:
                name.append(to_percent_str(rec.tax_final_percentage))
            result.append((rec.id, '%i: %s' % (rec.year, ' -> '.join(name))))
        return result
