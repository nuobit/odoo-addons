# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields, _
from odoo.exceptions import UserError

import re


class SaleOrderEmail(models.Model):
    _name = 'sale.order.email'
    _order = 'date desc'
    _rec_name = 'number'

    name = fields.Char(string='Subject')
    email_name = fields.Char(string='Name', required=False)
    email_from = fields.Char(string='From', required=True)
    email_domain = fields.Char(string='Domain', compute='_compute_email_domain', store=True,
                               readonly=True)

    @api.depends('email_from')
    def _compute_email_domain(self):
        for rec in self:
            m = re.match(r'^ *[^@]+@(.+) *$', rec.email_from)
            if not m:
                raise UserError("Incorrect e-mail format '%s'" % rec.email_from)
            rec.email_domain = m.group(1)

    date = fields.Datetime(string='Date', required=True)
    number = fields.Char(string='Number', required=True)

    body = fields.Text(string='Body')

    datas = fields.Binary(string="File", attachment=True, required=True)
    datas_fname = fields.Char(string='Filename', required=True, readonly=True)

    message_id = fields.Char(string='Message ID', required=True, readonly=True)

    source_id = fields.Many2one(comodel_name='sale.order.email.source',  # required=True,
                                ondelete='restrict', string="Source", readonly=True)

    _sql_constraints = [
        ('message_id_uniq', 'unique (message_id)', 'The message ID must be unique!'),
        ('source_number_uniq', 'unique (source_id, number)',
         'The number must be unique for each source!'),
        ('source_datas_fname_uniq', 'unique (source_id, datas_fname)',
         'The filename must be unique for each source!'),
    ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '%s@%s' % (record.source_id.name, record.number)
            vals.append((record.id, name))

        return vals

    @api.constrains('number')
    def _check_number(self):
        if self.number and len(self.number) != len(self.number.strip()):
            raise ValueError("The number is not valid, it should not have leading or trailing spaces")
