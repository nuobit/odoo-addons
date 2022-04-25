# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from odoo.addons.component.core import Component

from odoo import models, fields, api, exceptions, _

from ...components.adapter import api_handle_errors

_logger = logging.getLogger(__name__)


class AmbugestBackend(models.Model):
    _name = 'ambugest.backend'
    _inherit = 'connector.backend'

    _description = 'Ambugest Backend Configuration'

    @api.model
    def _select_state(self):
        """Available States for this Backend"""
        return [('draft', 'Draft'),
                ('checked', 'Checked'),
                ('production', 'In Production')]

    name = fields.Char('Name', required=True)

    server = fields.Char('Server', required=True)
    port = fields.Integer('Port', required=True)

    database = fields.Char('Database', required=True)
    schema = fields.Char('Schema', required=True)

    version = fields.Text('Version', readonly=True)

    username = fields.Char('Username', required=True)
    password = fields.Char('Password', required=True)

    company_id = fields.Many2one(
        comodel_name='res.company',
        index=True,
        required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'ambugest.backend'),
        string='Company',
    )

    ambugest_company_id = fields.Integer('Ambugest company ID', required=True)

    active = fields.Boolean(
        string='Active',
        default=True
    )
    state = fields.Selection(
        selection='_select_state',
        string='State',
        default='draft'
    )

    import_services_since_date = fields.Datetime('Import Services since')
    import_customers_since_date = fields.Datetime('Import Customers since')
    import_products_since_date = fields.Datetime('Import Products since')

    @api.multi
    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({'state': 'draft', 'version': None})

    @api.multi
    def _check_connection(self):
        self.ensure_one()
        with self.work_on('ambugest.backend') as work:
            component = work.component_by_name(name='ambugest.adapter.test')
            with api_handle_errors('Connection failed'):
                self.version = component.get_version()

    @api.multi
    def button_check_connection(self):
        self._check_connection()
        self.write({'state': 'checked'})

    @api.multi
    def import_products_since(self):
        for rec in self:
            since_date = rec.import_products_since_date
            self.env['ambugest.product.template'].with_delay(
            ).import_products_since(
                backend_record=rec, since_date=since_date)

        return True

    @api.multi
    def import_customers_since(self):
        for rec in self:
            since_date = rec.import_customers_since_date
            self.env['ambugest.res.partner'].with_delay(
            ).import_customers_since(
                backend_record=rec, since_date=since_date)

        return True

    @api.multi
    def import_services_since(self):
        for rec in self:
            since_date = rec.import_services_since_date
            self.env['ambugest.sale.order'].with_delay(
            ).import_services_since(
                backend_record=rec, since_date=since_date)

        return True

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

    @api.model
    def _scheduler_import_customers(self):
        company_id = self.get_current_user_company()

        domain = [
            ('company_id', '=', company_id.id)
        ]

        self.search(domain).import_customers_since()

    @api.model
    def _scheduler_import_services(self):
        company_id = self.get_current_user_company()

        domain = [
            ('company_id', '=', company_id.id)
        ]

        self.search(domain).import_services_since()
