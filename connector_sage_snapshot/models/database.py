# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class Database(models.Model):
    _name = 'connector.sage.snapshot.database'
    _description = 'Snapshot databases'

    name = fields.Char(string='Name')

    year = fields.Integer(string='Year', required=True)
    month = fields.Integer(string='Month', required=True)

    datas = fields.Binary(string="Database", attachment=True, required=True)
    datas_fname = fields.Char(string='Filename', required=True)

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get())

    _sql_constraints = [
        ('csnd_uniq', 'unique(company_id, month, year)',
         'Already exists another databse with the same month and year for the same company!!'),
    ]
