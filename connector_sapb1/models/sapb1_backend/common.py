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
    _order = 'sequence'

    @api.model
    def _select_state(self):
        return [('draft', 'Draft'),
                ('checked', 'Checked'),
                ('production', 'In Production')]

    name = fields.Char('Name', required=True)

    sequence = fields.Integer('Sequence', required=True, default=1)

    company_id = fields.Many2one(
        comodel_name='res.company',
        index=True,
        required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'sapb1.backend'),
        string='Company',
    )

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

    # data attributes
    import_products_since_date = fields.Datetime('Import Products since')

    # data methods
    @api.multi
    def import_products_since(self):
        for rec in self:
            since_date = fields.Datetime.from_string(rec.import_products_since_date)
            self.env['sapb1.lighting.product'].with_delay(
            ).import_products_since(
                backend_record=rec, since_date=since_date)

        return True

    # Scheduler methods
    @api.model
    def get_current_user_company(self):
        if self.env.user.id == self.env.ref('base.user_root').id:
            raise exceptions.ValidationError(_("The cron user cannot be admin"))

        return self.env.user.company_id

    @api.model
    def _scheduler_import_products(self):
        company_id = self.get_current_user_company()
        domain = [
            ('company_id', '=', company_id.id)
        ]
        self.search(domain).import_products_since()
