# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class SaleOrderEmail(models.Model):
    _name = 'sale.order.email'
    _order = 'date desc'

    name = fields.Char(string='Subject')
    email_from = fields.Char(string='From', required=True)
    date = fields.Datetime(string='Date', required=True)

    body = fields.Text(string='Body')

    datas = fields.Binary(string="File", attachment=True, required=True)
    datas_fname = fields.Char(string='Filename', required=True, readonly=True)

    message_id = fields.Char(string='Message ID', required=True, readonly=True)

    _sql_constraints = [
        ('message_id_uniq', 'unique (message_id)', 'The message ID must be unique!'),
        ('datas_fname_uniq', 'unique (datas_fname)', 'The filename must be unique!'),
    ]
