# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)


class SapB1Backend(models.Model):
    _name = 'sapb1.backend'
    _inherit = 'connector.backend'

    _description = 'SAP B1 Backend Configuration'

    @api.model
    def _select_state(self):
        return [('draft', 'Draft'),
                ('checked', 'Checked'),
                ('production', 'In Production')]

    name = fields.Char('Name', required=True)

    sequence = fields.Integer('Sequence', required=True, default=1)

    # fileserver
    fileserver_host = fields.Char('Server', required=True)
    fileserver_port = fields.Integer('Port', required=True)

    fileserver_username = fields.Char('Username', required=True)
    fileserver_password = fields.Char('Password', required=True)

    fileserver_basepath = fields.Char('Base path', required=True)

    fileserver_version = fields.Text('Version', readonly=True)

    # database
    db_host = fields.Char('Server', required=True)
    db_port = fields.Integer('Port', required=True)

    db_schema = fields.Char('Schema', required=True)

    db_username = fields.Char('Username', required=True)
    db_password = fields.Char('Password', required=True)

    db_version = fields.Text('Version', readonly=True)

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
        self.write({'state': 'draft', 'version': None})

    @api.multi
    def _check_connection(self):
        self.ensure_one()
        # TODO

    @api.multi
    def button_check_connection(self):
        self._check_connection()
        self.write({'state': 'checked'})
