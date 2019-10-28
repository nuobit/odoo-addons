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
