# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, exceptions, _

from . import ertransit

import logging

_logger = logging.getLogger(__name__)


class ERTransitBackend(models.Model):
    _name = 'ertransit.backend'
    _inherit = 'connector.backend'

    _description = 'ERTransit / Erhardt Backend Configuration'

    @api.model
    def _select_state(self):
        return [('draft', 'Draft'),
                ('checked', 'Checked'),
                ('production', 'In Production')]

    name = fields.Char('Name', required=True)

    sequence = fields.Integer('Sequence', required=True, default=1)

    username = fields.Char('Username', required=True)
    password = fields.Char('Password', required=True)

    output = fields.Text('Output', readonly=True)

    active = fields.Boolean(
        string='Active',
        default=True
    )
    state = fields.Selection(
        selection='_select_state',
        string='State',
        default='draft'
    )

    @api.multi
    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({'state': 'draft', 'output': None})

    @api.multi
    def _check_connection(self):
        self.ensure_one()
        er = ertransit.ERTransit(username=self.username, password=self.password)

        if not er.login():
            raise exceptions.ValidationError("Error on logging in")

        if not er.logout():
            raise exceptions.ValidationError("Error on logging out")

        self.output = "OK"

    @api.multi
    def button_check_connection(self):
        self._check_connection()
        self.write({'state': 'checked'})
