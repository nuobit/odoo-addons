# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from odoo.addons.component.core import Component

from odoo import models, fields, api, exceptions, _

from ...components.adapter import api_handle_errors

_logger = logging.getLogger(__name__)


class Backend(models.Model):
    _name = 'sage.backend'
    _inherit = 'connector.backend'

    _description = 'Sage Backend Configuration'

    @api.model
    def _select_state(self):
        """Available States for this Backend"""
        return [('draft', 'Draft'),
                ('checked', 'Checked'),
                ('production', 'In Production')]

    name = fields.Char('Name', required=True)

    server = fields.Char('Server')
    port = fields.Integer('Port')

    database = fields.Char('Database')
    schema = fields.Char('Schema')

    username = fields.Char('Username')
    password = fields.Char('Password')

    company_id = fields.Many2one(
        comodel_name='res.company',
        index=True,
        required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'sage.backend'),
        string='Company',
    )

    sage_company_id = fields.Integer('Sage company ID', required=True)

    active = fields.Boolean(
        string='Active',
        default=True
    )
    state = fields.Selection(
        selection='_select_state',
        string='State',
        default='draft'
    )

    import_employees_since_date = fields.Datetime('Import employees since')
    import_labour_agreements_since_date = fields.Datetime('Import labour agreements since')

    #import_contacts_since_date = fields.Datetime('Import contacts since')

    @api.multi
    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    # @api.multi
    # def _check_connection(self):
    #     self.ensure_one()
    #     with self.work_on('sage.backend') as work:
    #         component = work.component_by_name(name='sage.adapter.test')
    #         with api_handle_errors('Connection failed'):
    #             component.check()

    @api.multi
    def button_check_connection(self):
        self._check_connection()
        # raise exceptions.UserError(_('Connection successful'))
        self.write({'state': 'checked'})

    @api.multi
    def import_employees_since(self):
        for rec in self:
            since_date = rec.import_employees_since_date
            self.env['sage.hr.employee'].with_delay(
            ).import_employees_since(
                backend_record=rec, since_date=since_date)

        return True

    @api.multi
    def import_labour_agreements_since(self):
        for rec in self:
            since_date = rec.import_labour_agreements_since_date
            self.env['sage.payroll.sage.labour.agreement'].with_delay(
            ).import_labour_agreements_since(
                backend_record=rec, since_date=since_date)

        return True

    # @api.multi
    # def import_contacts_since(self):
    #     for rec in self:
    #         since_date = rec.import_contacts_since_date
    #         self.env['sage.res.partner'].with_delay(
    #         ).import_contacts_since(
    #             backend_record=rec, since_date=since_date)
    #
    #     return True

    @api.model
    def _scheduler_import_employees(self, domain=None):
        self.search(domain or []).import_employees_since()

    @api.model
    def _scheduler_import_labour_agreements(self, domain=None):
        self.search(domain or []).import_labour_agreements_since()

    # @api.model
    # def _scheduler_import_contacts(self, domain=None):
    #     self.search(domain or []).import_contacts_since()

# class NoModelAdapter(Component):
#     """ Used to test the connection """
#     _name = 'sage.adapter.test'
#     _inherit = 'sage.adapter'
#     _apply_on = 'sage.backend'
#
#     _sage_model = ''
